import pygame, os, sys, csv
from pygame.locals import *
import moderngl as mgl
from array import array
from Config import *
import Config as conf
import numpy as np

filters_keys = {'nearest': mgl.NEAREST, 'linear': mgl.LINEAR}
rendermode_keys = {'trianglestrip': mgl.TRIANGLE_STRIP, 'linestrip': mgl.LINE_STRIP}

vec2 = pygame.math.Vector2
vec3 = pygame.math.Vector3
rect = pygame.Rect

class Initialize:
    def __init__(self):
        pygame.init()
        conf.program = self
        conf.io = Io
        conf.play = Play()
        conf.initialw, conf.initialh, conf.initialscalex, conf.initialscaley = w, h, scalex, scaley
        
        self.screen = pygame.display.set_mode((w, h), DOUBLEBUF | OPENGL | RESIZABLE | SRCALPHA)
        self.clock = pygame.time.Clock()
        self.render = pygame.Surface((w/scalex, h/scaley), SRCALPHA)
        
        self.ctx = mgl.create_context()
        self.quad_buffer = self.ctx.buffer(data=array('f', [
            -1.0, 1.0, 0.0, 0.0, #topleft
            1.0, 1.0, 1.0, 0.0,  #topright
            -1.0, -1.0, 0.0, 1.0,#bottomleft
            1.0, -1.0, 1.0, 1.0  #bottomright
        ])) #postion , uv coords
        self.program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
        self.render_object = self.ctx.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])
        
        self.surfaces = {}
        self.animations = {}
        self.maps = {}
        self.sprites = {}
        for scene in scenes:
            conf.play.Scene(scene, 'addScene')
        for img in conf.images:
            self.LoadImage(conf.images[img], img)
        for anim in animations:
            self.LoadAnimation(animations[anim], anim)
        for map in maps:
            self.LoadMap(maps[map]['file'], map)
    
    def generateMaps(self):
        for mapK in self.maps:
            mapL = self.maps[mapK]
            s = conf.play.Scene(maps[mapK]['scene'])
            s.addComponentGroup(maps[mapK]['group'])
            for k in maps[mapK]['mapping']:
                s.addComponentGroup(maps[mapK]['group']+k)
            for i in range(len(mapL)):
                for j in range(len(mapL[0])):
                    if i != len(mapL)-1:
                        if mapL[i][j] in maps[mapK]['mapping']:
                            c = self.sprites[maps[mapK]['mapping'][mapL[i][j]]]((i,j))
                            s.addGroupedComponent(c, maps[mapK]['group'])
                            s.addGroupedComponent(c, maps[mapK]['group']+mapL[i][j])
                    else:
                        if mapL[i][j-1] in maps[mapK]['mapping']:
                            c = self.sprites[maps[mapK]['mapping'][mapL[i][j-1]]]((i,j-1))
                            s.addGroupedComponent(c, maps[mapK]['group'])
                            s.addGroupedComponent(c, maps[mapK]['group']+mapL[i][j-1])
    
    def surface_to_texture(self, surface: pygame.Surface):
        texture = self.ctx.texture(surface.get_size(), 4)
        texture.filter = (filters_keys[conf.texfilter], filters_keys[conf.texfilter])
        texture.swizzle = conf.texswizzle
        texture.write(surface.get_view('1'))
        return texture

    def setSprite(self, sprite, name):
        self.sprites[name] = sprite
        return self
    
    def LoadImage(self, imagepath, imagekey):
        self.surfaces[imagekey] = pygame.image.load(imagepath)

    def LoadAnimation(self, filespath, animationkey):
        self.animations[animationkey] = []
        for file in os.listdir(filespath):
            self.animations[animationkey].append(filespath+':'+file)
            self.surfaces[filespath+':'+file] = pygame.image.load(filespath+'/'+file)

    def LoadMap(self,filepath,key):
        with open(filepath) as f:
            self.maps[key] = list(csv.reader(f))

    def clear_screen(self):
        self.render.fill(conf.clearcolor)

    def draw(self, surfacekey, pos):
        self.render.blit(self.surfaces[surfacekey],(pos[0],pos[1]))

    def clockTick(self):
        conf.dt = min(self.clock.get_time()/1000, conf.maxdt)

    def update(self):
        
        frametex = self.surface_to_texture(self.render)
        frametex.use(0)
        self.program['tex'] = 0
        for param in conf.fragmentParameters:
            self.program[param] = conf.fragmentParameters[param]
        self.render_object.render(mode=rendermode_keys[conf.rendermode])
        
        pygame.display.flip()
        frametex.release()
        self.clock.tick(fps)
        self.clockTick()
        self.clear_screen()
        
        conf.w, conf.h = pygame.display.get_window_size()
        conf.scalex = conf.initialscalex*conf.w/conf.initialw
        conf.scaley = conf.initialscaley*conf.h/conf.initialh

class Io:
    def exit(code=0):
        pygame.quit()
        sys.exit(code)
    
    def mousePos(relative:bool=True):
        mx, my = pygame.mouse.get_pos()
        return (mx/conf.scalex, my/conf.scaley)
    
    def mousePressed():
        return pygame.mouse.get_pressed()
    
    def keyPressed(key:str):
        return pygame.key.get_pressed()[pygame.key.key_code(key)]

class SceneHandle:
    def __init__(self):
        self.ComponentGroups = {
            'components': []
                            }
        self.Components = {}
        
        self.Events = {}
        
    def addComponentGroup(self, groupName='components'):
        self.ComponentGroups[groupName] = []
        return self
    
    def addGroupedComponent(self, component, groupName='components'):
        self.ComponentGroups[groupName].append(component)
        self.Components[f'{groupName}-{len(self.ComponentGroups[groupName])}'] = component
        return self
    
    def addComponent(self, component, componentName='component'):
        self.Components[componentName] = component
        return self
    
    def drawGroup(self,groupName):
        for sprite in self.ComponentGroups[groupName]:
            sprite.render()
        return self
    
    def animateComponentGroup(self,groupName):
        for sprite in self.ComponentGroups[groupName]:
            sprite.animate()
        return self

    def addEvent(self, eventName, event):
        conf.play.customEvents += 1
        eventu = pygame.USEREVENT+conf.play.customEvents
        self.Events[eventName] = {
            'event':eventu,
            'condition': (event,pygame.event.Event(eventu)),
            'conseq':[]
        }
        return self
    
    def addConsequence(self, event, cons):
        self.Events[event]['conseq'].append(cons)
        return self
    
    def run(self):
        pass
    
    def update(self):
        map(pygame.event.post, [e for (c,e) in [con['confition'] for con in self.Events] if c()])
        
        for comp in self.Components.values():
            comp.update()
        for event in pygame.event.get():
            for Event in self.Events:
                if event.type == Event['event']:
                    for conseq in Event['conseq']:
                        conseq()
        self.run(self)
        return self
    
    def __getitem__(self, item):
        if item in self.Components:
            return self.Components[item]
        return self.ComponentGroups[item]

class Play:
    def __init__(self):
        self.scenes = {
            'default':  SceneHandle()
            }
        self.scene = 'default'
        self.customEvents = 0
        self.echos = {
            'scalex': False,
            'scaley': False
        }
    
    def Scene(self, sceneName='default',work=nillVal,handle=SceneHandle):
        '''addScene: set handle for new or existing scene
{nillVal}: return scene handle
setScene: set scene
        '''
        if work == nillVal:
            return self.scenes[sceneName]
        elif work == 'addScene':
            self.scenes[sceneName] = handle()
        elif work == 'setScene':
            self.scene = sceneName
        return self

    def update(self):
        self.scenes[self.scene].update()
        for e in self.echos:
            self.echos[e] = False

    def __getitem__(self, item) -> SceneHandle:
        return self.scenes[item]
