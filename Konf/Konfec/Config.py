#---------   Render Config   ---------
fps = 60

w, h = 1280, 720
scalex, scaley = 1, 1
clearcolor = (0,0,0,0)

fragmentParameters = {
}
rendermode = 'trianglestrip'

texfilter = 'nearest'
texswizzle = 'BGRA'

#----------    Loads    ----------
images = {
}
animations = {
}
maps = {    
}

#----------    Shaders    ----------
vert_shader = '''
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;
varying vec2 vTexCoord;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}
'''

frag_shader = '''
#version 330 core

uniform sampler2D tex;

in vec2 uvs;
out vec4 f_color;

void main() {
    f_color = vec4(texture2D(tex, uvs).rgb, 1.0);
}
'''

#----------   Initialization   ----------
program = None
io = None
play = None
dt = 1/max(fps,1)
nillVal = '123456789000000000123456789'
