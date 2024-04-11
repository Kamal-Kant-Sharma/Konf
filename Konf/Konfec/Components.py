from Conf.Program import pygame, conf, np

class Sprite:
    def __init__(self, defaultkey, pos=(0,0)):
        self.animations = {}
        self.defaultkey = defaultkey
        self.image = defaultkey
        self.state = 'none'
        self.pos = pygame.math.Vector2(pos)
        self.features = {
            'animation': None,
            'frame': 0}
    
    def Animation(self, animationname, key,fps=1,loop=True):
        if key in conf.program.animations:
            self.animations[animationname] = {
                'keys': conf.program.animations[key],
                'fps': fps,
                'loop': loop,
            }
        else:
            self.animations[animationname] = {
                'keys': [key],
                'fps': fps,
                'loop': loop,
            }
        return self

    def State(self,state=conf.nillVal):
        if state != conf.nillVal:
            self.state = state
            return self
        return self.state
    
    def render(self, animate=True):
        if animate:
            self.animate()
        conf.program.draw(self.image,self.pos)
        return self
    
    def animate(self,dt=conf.dt):
        if self['animation'] in self.animations.keys():
            animation = self.animations[self['animation']]
            self['frame'] += dt*animation['fps']
            
            if self['frame'] >= len(animation['keys']):
                self['frame'] = len(animation['keys'])-1
                if animation['loop']:
                    self['frame'] = 0
            
            self.image = animation['keys'][int(np.floor(self['frame']))]
        else:
            self.image = self.defaultkey
        return self
    
    def __getitem__(self, item):
        return self.features[item]
    
    def __setitem__(self, item, val):
        self.features[item] = val

    def update(self):
        pass
