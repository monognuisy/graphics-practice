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


def key_callback(window, key, scancode, action, mods):
    global keyInput
    if key == glfw.KEY_1 and action == glfw.PRESS:
        keyInput = 1
    if key == glfw.KEY_2 and action == glfw.PRESS:
        keyInput = 2
    if key == glfw.KEY_3 and action == glfw.PRESS:
        keyInput = 3
    if key == glfw.KEY_4 and action == glfw.PRESS:
        keyInput = 4
    if key == glfw.KEY_5 and action == glfw.PRESS:
        keyInput = 5
    if key == glfw.KEY_6 and action == glfw.PRESS:
        keyInput = 6
    if key == glfw.KEY_7 and action == glfw.PRESS:
        keyInput = 7
    if key == glfw.KEY_8 and action == glfw.PRESS:
        keyInput = 8
    if key == glfw.KEY_9 and action == glfw.PRESS:
        keyInput = 9
    if key == glfw.KEY_0 and action == glfw.PRESS:
        keyInput = 0


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # draw triangle
    glBegin(glPrimitiveTypes[keyInput])
    glColor3ub(255, 255, 255)

    vertexes = np.radians((np.arange(12)) * 30)
    xVertexes = np.cos(vertexes)
    yVertexes = np.sin(vertexes)

    for n in range(12):
        glVertex2fv([xVertexes[n], yVertexes[n]])

    glEnd()


def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(480, 480, "2021031685-2-2", None, None)
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

        render()
        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
