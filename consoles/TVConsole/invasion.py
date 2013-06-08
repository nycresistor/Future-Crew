# This code is based on a port of the Hello_Triangle example from the
# OpenGL ES 2.0 Programming Guide.


from array import array

from pogles.egl import *
from pogles.gles2 import *

import pygame.font as font
from pygame import Surface
import pygame.image

font.init()
f = font.SysFont('LCD',120)

# Create a shader object, load the shader source, and compile the shader.
def load_shader(shader_type, shader_source):
    # Create the shader object.
    shader = glCreateShader(shader_type)
    if shader == 0:
        return 0
    # Load the shader source.
    glShaderSource(shader, shader_source)
    # Compile the shader.
    glCompileShader(shader)
    # Check the compile status.
    compiled, = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not compiled:
        glDeleteShader(shader);
        raise GLException(
                "Error compiling shader:\n%s" % glGetShaderInfoLog(shader))
    return shader;


text_vertex_shader_src="""
attribute vec4 vPosition;
attribute vec2 TexCoordIn;
varying vec2 TexCoordOut;
 
void main()
{
    gl_Position = vPosition;
    TexCoordOut = TexCoordIn; 
}
"""

text_fragment_shader_src="""
varying lowp vec2 TexCoordOut;
uniform sampler2D Texture;
 
void main(void) {
    gl_FragColor = texture2D(Texture, TexCoordOut); // vec4(0.2,TexCoordOut.x,TexCoordOut.y,1.0) *
    gl_FragColor.a = 0.5;
}
"""

text_bindings = [(0, 'vPosition'), (1, 'TexCoordIn')]

# Create the program and shaders.
def create_program(vertex_src,fragment_src,bindings=[]):
    # Load the vertex/fragment shaders.
    vertex_shader = load_shader(GL_VERTEX_SHADER, vertex_src)
    fragment_shader = load_shader(GL_FRAGMENT_SHADER, fragment_src);
    # Create the program.
    program = glCreateProgram()
    if program == 0:
        return 0
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    for (index,name) in bindings:
        glBindAttribLocation(program, index, name)
    # Link the program.
    glLinkProgram(program)
    # Check the link status.
    linked, = glGetProgramiv(program, GL_LINK_STATUS)
    if not linked:
        glDeleteProgram(program)
        raise GLException(
                "Error linking program:\n%s" % glGetProgramInfoLog(program))
    glClearColor(0.0, 0.0, 0.0, 0.0)
    return program


def make_text(text):
    img = f.render(text, True, (255,255,255,100))
    def power_up(x):
        s = 1
        while x != 0:
            s <<= 1
            x >>= 1
        return s
    sz = tuple(map(power_up,img.get_size()))
    sz = (max(sz),max(sz))
    s = Surface(sz,pygame.SRCALPHA,img)
    s.fill((100,0,0,50))
    s.blit(img,(0,0))
    return s

def set_text_slot(text,slot):
    s = make_text(text)
    sz = s.get_size()
    glActiveTexture(GL_TEXTURE0+slot)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, sz[0], sz[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(s,"RGBA",1))

def draw_text_slot(program,slot):
    z = -float(slot)/10.0
    vVertices = array('f', [-1.0, -1.0,  z,  0.0, 0.0,
                             1.0, -1.0,  z,  1.0, 0.0,
                            -1.0,  1.0,  z,  0.0, 1.0,
                             1.0,  1.0,  z,  1.0, 1.0])
    vIndices = array('H', [ 0, 2, 3, 0, 3, 1 ])
    # Load the vertex data.
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 4*5, vVertices)
    glVertexAttribPointer(1, 2, GL_FLOAT, False, 4*5, vVertices[3:])
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)

    glActiveTexture(GL_TEXTURE0+slot)
    glBindTexture(GL_TEXTURE_2D, textures[slot])
    l = glGetUniformLocation(program,"Texture")
    glUniform1i(l, slot);

    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_SHORT, vIndices)

# Draw a triangle using the shaders.
def draw(program,w,h):
    # Set the viewport.
    glViewport(0, 0, width, height)
    # Clear the color buffer.
    glClear(GL_COLOR_BUFFER_BIT)
    # Use the text program object.
    glUseProgram(text_program)
    draw_text_slot(text_program,0)
    draw_text_slot(text_program,1)

# Create an EGL rendering context and all associated elements.
def create_egl_context(native_window, attribs):
    # Get the default display.
    display = eglGetDisplay()
    # Initialize EGL.
    eglInitialize(display)
    # Choose the config.
    config = eglChooseConfig(display, attribs)[0]
    # Create a surface from the native window.
    surface = eglCreateWindowSurface(display, config, native_window, [])
    # Create a GL context.
    context = eglCreateContext(display, config, None,
            [EGL_CONTEXT_CLIENT_VERSION, 2])
    # Make the context current.
    eglMakeCurrent(display, surface, surface, context)
    return display, surface

textures = []
if __name__ == '__main__':

    import select
    import sys

    from pogles.platform import ppCreateNativeWindow

    native_window = ppCreateNativeWindow()
    display, surface = create_egl_context(native_window,
            [EGL_RED_SIZE, 5, EGL_GREEN_SIZE, 6, EGL_BLUE_SIZE, 5, EGL_SAMPLES, 4])

    width = eglQuerySurface(display, surface, EGL_WIDTH)
    height = eglQuerySurface(display, surface, EGL_HEIGHT)

    text_program = create_program(text_vertex_shader_src,
                                  text_fragment_shader_src,
                                  text_bindings)
    #f = font.SysFont('ParaAminobenzoic',120)

    textures = glGenTextures(2)
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    for i in range(len(textures)):
        glActiveTexture(GL_TEXTURE0 + i)
        glBindTexture(GL_TEXTURE_2D, textures[i])
        glTexParameteri ( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
        glTexParameteri ( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
    set_text_slot('hello hello',1)
    set_text_slot('robo robo',0)
    import time
    stamp = time.time()
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    while len(ready) == 0:
        draw(text_program, width, height)
        eglSwapBuffers(display, surface)
        if (time.time() - stamp) > 2:
            stamp = time.time()
            print "update"
        ready, _, _ = select.select([sys.stdin], [], [], 0)
