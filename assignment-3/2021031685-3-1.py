import glfw
from OpenGL.GL import *
import numpy as np

glPrimitiveTypes = [
    GL_POLYGON,
    GL_POINTS,
    GL_LINES,
    GL_LINE_STRIP,
    GL_LINE_LOOP,
    GL_TRIANGLES,
    GL_TRIANGLE_STRIP,
    GL_TRIANGLE_FAN,
    GL_QUADS,
    GL_QUAD_STRIP,
]

keyInput = 4


globalT = np.identity(3)


def key_callback(window, key, scancode, action, mods):
    global keyInput
    global globalT
    if key == glfw.KEY_A and action == glfw.PRESS:
        theta = np.radians(10)
        R = np.identity(3)
        R[:2, :2] = [[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]]
        globalT = globalT @ R
    if key == glfw.KEY_D and action == glfw.PRESS:
        theta = np.radians(-10)
        R = np.identity(3)
        R[:2, :2] = [[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]]
        globalT = globalT @ R
    if key == glfw.KEY_1 and action == glfw.PRESS:
        globalT = np.identity(3)
    if key == glfw.KEY_Q and action == glfw.PRESS:
        T = np.identity(3)
        T[:2, 2] = [-.1, 0.]

        globalT = T @ globalT 
    if key == glfw.KEY_E and action == glfw.PRESS:
        T = np.identity(3)
        T[:2, 2] = [.1, 0.]

        globalT = T @ globalT 
    if key == glfw.KEY_W and action == glfw.PRESS:
        S = np.identity(3)
        S[0, 0] = .9

        globalT = S @ globalT 
    if key == glfw.KEY_S and action == glfw.PRESS:
        theta = np.radians(10)
        R = np.identity(3)
        R[:2, :2] = [[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]]
        globalT = R @ globalT


def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv( (T @ np.array([.0,.5,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.0,.0,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.5,.0,1.]))[:-1] )
    glEnd()



def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(480, 480, "2021031685-3-1", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)
    # Make the window's context current
    glfw.make_context_current(window)

    glfw.swap_interval(1)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll events
        glfw.poll_events()
        # Render here, e.g. using pyOpenGL


        render(globalT)
        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
