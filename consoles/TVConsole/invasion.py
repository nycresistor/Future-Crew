# This code is based on a port of the Hello_Triangle example from the
# OpenGL ES 2.0 Programming Guide.
from future_client import FutureClient, Game, MessageSlot

from array import array

from pogles.egl import *
from pogles.gles2 import *

import pygame.font as font
from pygame import Surface
import pygame.image
import euclid

font.init()
f = font.Font('./LCD.ttf',48)

from itertools import chain
import time

def truncline(text, maxwidth):
        real=len(text)       
        stext=text           
        l=f.size(text)[0]
        cut=0
        a=0                  
        done=1
        old = None
        while l > maxwidth:
            a=a+1
            n=text.rsplit(None, a)[0]
            if stext == n:
                cut += 1
                stext= n[:-cut]
            else:
                stext = n
            l=f.size(stext)[0]
            real=len(stext)               
            done=0                        
        return real, done, stext             
        
def wrapline(text, maxwidth): 
    done=0                      
    wrapped=[]                  
                               
    while not done:             
        nl, done, stext=truncline(text, maxwidth) 
        wrapped.append(stext.strip())                  
        text=text[nl:]                                 
    return wrapped

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
varying mediump vec2 TexCoordOut;
uniform sampler2D Texture;
 
void main(void) {
    gl_FragColor = texture2D(Texture, TexCoordOut); // vec4(0.2,TexCoordOut.x,TexCoordOut.y,1.0) *
}
"""

text_bindings = [(0, 'vPosition'), (1, 'TexCoordIn')]

tri_vertex_shader_src = """
uniform mat4 mTransform;
uniform mat4 mPerspective;
attribute vec4 vPosition;
void main()
{
    gl_Position = mTransform * vPosition;
    gl_Position = mPerspective * mTransform * vPosition;
}
"""
   
tri_fragment_shader_src = """
precision mediump float;
void main()
{
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
"""

tri_bindings = [(0, 'vPosition')]

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



class TextSlot(MessageSlot):
    def __init__(self,program,index,texture):
        self.prog = program
        self.idx = index
        self.tex = texture
        self.x = 0
        self.y = 0
        self.queue_text = ''
        super(TextSlot, self).__init__()

    def on_message(self,text):
        if text == None:
            text = ''
        self.queue_text = text

    def update(self):
        if self.queue_text == None:
            return
        elif self.queue_text == '':
            self.set_text('')
            self.queue_text = None
        else:
            self.set_text(self.queue_text)
            self.queue_text = None

    def set_text(self,text):
        sz = (512,256)
        s = Surface(sz,pygame.SRCALPHA)
        s.fill((255,0,0,50))
        lines = wrapline(text,512)
        y = 0
        for line in lines:
            img = f.render(line, True, (255,255,255,100))
            (_, h) = img.get_size()
            s.blit(img,(0,y))
            y += h
        print "blitting",text,"on",self.idx
        glActiveTexture(GL_TEXTURE0+self.idx)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, sz[0], sz[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(s,"RGBA",1))

    def draw_text_slot(self):
        z = 0
        e = 0.8
        top = bottom = 0
        if self.idx == 0:
            top = e
        else:
            bottom = -e
        vVertices = array('f', [-e, bottom,  z,
                                 e, bottom,  z,
                                 -e, top,  z,
                                 e,  top,  z,])
        vTex = array('f', [ 0.0, 0.0,
                            1.0, 0.0,
                            0.0, 1.0,
                            1.0, 1.0])
        vIndices = array('H', [ 0, 2, 3, 0, 3, 1 ])
        # Load the vertex data.
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, vVertices)
        glVertexAttribPointer(1, 2, GL_FLOAT, False, 0, vTex)
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)

        glActiveTexture(GL_TEXTURE0+self.idx)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        l = glGetUniformLocation(self.prog,"Texture")
        glUniform1i(l,self.idx);

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_SHORT, vIndices)

slots = []

def matToList(m):
	m = m.transposed()
	return [m.a,m.b,m.c,m.d, m.e,m.f,m.g,m.h,
		m.i,m.j,m.k,m.l, m.m,m.n,m.o,m.p]

translation = euclid.Vector3()

zstamp = time.time()

def draw_triangle():
    vVertices = array('f', [ 0.0,  0.5,  0.0, 
                             -0.5, -0.5,  0.0,
                             0.5, -0.5,  0.0])
    glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, vVertices)
    glEnableVertexAttribArray(0)
    tloc = glGetUniformLocation(tri_program,"mTransform")
    ploc = glGetUniformLocation(tri_program,"mPerspective")
    m = euclid.Matrix4()
    zdist = (time.time()-zstamp)/5.0
    print zdist
    m.translate(0.5,0.1,-5.0+zdist)
    glUniformMatrix4fv(tloc, False, matToList(m))
    p = euclid.Matrix4.new_perspective(90.0,4.0/3.0,1.0,10.0)
    glUniformMatrix4fv(ploc, False, matToList(p))
    glDrawArrays(GL_TRIANGLES, 0, 3)

# Draw a triangle using the shaders.
def draw(program,w,h):
    # Set the viewport.
    glViewport(0, 0, width, height)
    # Clear the color buffer.
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(tri_program)
    draw_triangle()
    # Use the text program object.
    glUseProgram(text_program)
    for slot in slots:
        slot.update()
        slot.draw_text_slot()

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

    tri_program = create_program(tri_vertex_shader_src,
                                 tri_fragment_shader_src,
                                 tri_bindings)
    #f = font.SysFont('ParaAminobenzoic',120)

    textures = glGenTextures(2)
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    for i in range(len(textures)):
        glActiveTexture(GL_TEXTURE0 + i)
        glBindTexture(GL_TEXTURE_2D, textures[i])
        glTexParameteri ( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
        glTexParameteri ( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
        slots.append(TextSlot(text_program,i,textures[i]))
    slots[0].set_text('hello hello')
    slots[1].set_text('robo robo')
    stamp = time.time()
    ready, _, _ = select.select([sys.stdin], [], [], 0)

    fc = FutureClient(name='TV client')
    fc.available_games = []
    fc.message_slots = slots
    fc.start()

    try:
        while len(ready) == 0:
            draw(text_program, width, height)
            eglSwapBuffers(display, surface)
            ready, _, _ = select.select([sys.stdin], [], [], 0)
    finally:
        fc.quit()
