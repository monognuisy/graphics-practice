import glfw
from OpenGL.GL import *
import numpy as np
from OpenGL.GLU import *

gCamAng = 1
gCamHeight = 1.

def createVertexArrayIndexed():
    varr = np.array([
        (0, 0, 0),      # v0
        (1.5, 0, 0),    # v1
        (0, 1.5, 0),    # v2
        (0, 0, 1.5),    # v3
    ], 'float32')

    iarr = np.array([
        (0, 1, 2),
        (0, 3, 2),
        (1, 2, 3),
    ])

    return varr, iarr

def render():
    global gCamAng, gCamHeight
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    glLoadIdentity()
    gluPerspective(45, 1, 1, 10)
    gluLookAt(5*np.sin(gCamAng),gCamHeight,5*np.cos(gCamAng), 0,0,0, 0,1,0)
    drawFrame()
    glColor3ub(255, 255, 255)
    # drawCube_glVertex()
    drawCube_glDrawArrays()

def drawCube_glDrawArrays():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY) # Enable it to use vertex array

    # print(varr)
    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
    # glDrawArrays(GL_TRIANGLES, 0, int(varr.size/3))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)

gVertexArrayIndexed = None
gIndexArray = None
def main():
    global gVertexArrayIndexed, gIndexArray

    if not glfw.init():
        return
    
    window = glfw.create_window(640,640,'Lecture10', None,None)

    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    gVertexArrayIndexed, gIndexArray = createVertexArrayIndexed()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    
    glfw.terminate()

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([1.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,1.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,1.]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight

    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key==glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key==glfw.KEY_2:
            gCamHeight += .1
        elif key==glfw.KEY_W:
            gCamHeight += -.1

if __name__ == "__main__":
    main()

