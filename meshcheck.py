#!/usr/bin/python

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys

_inited = False

def main():
    # initialize GLUT window
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow("meshcheck")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)

    # start meshcheck viewer
    glutMainLoop()

def draw_background(top_color, bottom_color):
    '''
    Clear color/depth and draw a background quad.
    '''
    # clear color and depth, disable lighting
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glDisable(GL_LIGHTING)

    # set up ortho view
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1, 0, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # draw a quad with a top to bottom gradient
    glBegin(GL_QUADS)
    glColor3fv(bottom_color)
    glVertex2f(0, 0)
    glVertex2f(1, 0)
    glColor3fv(top_color)
    glVertex2f(1, 1)
    glVertex2f(0, 1)
    glEnd()

    # clear the depth buffer
    glClear(GL_DEPTH_BUFFER_BIT)

    # reset matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_mesh():
    glEnable(GL_LIGHTING)

def init_state():
    global _inited
    if not _inited:
        _inited = True
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    lightZeroPosition = [10.,4.,10.,1.]
    lightZeroColor = [0.8,1.0,0.8,1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)        

def display():
    init_state()
    draw_background((0.75, 0.75, 0.75),
                    (0.5, 0.5, 0.5))
    draw_mesh()
    color = [1.0,0.,0.,1.]
    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
    glutSolidSphere(2,20,20)
    glutSwapBuffers()
    return

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, width*1.0/height, 1, 40)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0,0,10,
              0,0,0,
              0,1,0)
    #glMatrixMode(GL_PROJECTION)
    #glLoadIdentity()
    #glFrustum (-1.0, 1.0, -1.0, 1.0, 1.5, 20.0);
    #glMatrixMode (GL_MODELVIEW);

if __name__ == '__main__': main()
