#!/usr/bin/python

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import json
import math
import numpy
import pprint
import sys

class Context:
    class Camera:
        def __init__(self):
            self.elevation = 0
            self.angle = 0
            self.distance = 5

        def location(self):
            l = numpy.array((math.sin(self.angle),
                             math.sin(self.elevation),
                             math.cos(self.angle)))
            return l * self.distance / numpy.linalg.norm(l)

    class Window:
        def __init__(self):
            self.mouse = {
                GLUT_LEFT_BUTTON: GLUT_UP,
                GLUT_MIDDLE_BUTTON: GLUT_UP,
                GLUT_RIGHT_BUTTON: GLUT_UP}
            self.mouse_last = {
                GLUT_LEFT_BUTTON: (0, 0),
                GLUT_MIDDLE_BUTTON: (0, 0),
                GLUT_RIGHT_BUTTON: (0, 0)}

    def __init__(self):
        self.camera = self.Camera()
        self.inited = False
        self.mesh = None
        self.window = self.Window()

C = Context()

class Mesh:
    def __init__(self):
        self.verts = {}
        self.faces = {}

    def add_vert(self, name, x, y, z):
        if name in self.verts:
            raise Exception('Duplicate vertex name')
        self.verts[name] = numpy.array([x, y, z])

    def add_face(self, name, verts):
        if name in self.faces:
            raise Exception('Duplicate face name')
        for v in verts:
            if v not in self.verts:
                raise Exception('Unknown vertex ' + str(v))
        self.faces[name] = verts

    def face_normal(self, name):
        v = self.faces[name]
        # assuming triangle for now
        v1 = self.verts[v[1]] - self.verts[v[0]]
        v2 = self.verts[v[1]] - self.verts[v[2]]
        return numpy.cross(v1, v2)

def load_json_mesh(text):
    mesh = Mesh()
    json_mesh = json.loads(text)
    verts = json_mesh['verts']
    faces = json_mesh['faces']

    for v in verts:
        mesh.add_vert(v, *verts[v])

    for f in faces:
        mesh.add_face(f, faces[f])

    return mesh

def main():
    global C

    # get mesh
    C.mesh = load_json_mesh(open('test.json').read())

    # initialize GLUT window
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow("meshcheck")

    # GLUT callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(handle_mouse)
    glutMotionFunc(handle_motion)

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
    global C
    
    glLoadIdentity()
    eye = C.camera.location()
    gluLookAt(eye[0], eye[1], eye[2],
              0,0,0,
              0,1,0)

    # set light position
    glEnable(GL_LIGHTING)
    glLightfv(GL_LIGHT0, GL_POSITION, -eye)

    color = [1.0,0.,0.,1.]
    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)

    for f in C.mesh.faces:
        glBegin(GL_POLYGON)
        glNormal3fv(C.mesh.face_normal(f))
        for v in C.mesh.faces[f]:
            glVertex3fv(C.mesh.verts[v])
        glEnd()

def init_state():
    global C
    if not C.inited:
        C.inited = True
    #glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    lightZeroColor = [0.8,1.0,0.8,1.0]
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)        

def display():
    init_state()
    draw_background((0.75, 0.75, 0.75),
                    (0.5, 0.5, 0.5))
    draw_mesh()
    glutSwapBuffers()
    return

def reshape(width, height):
    global C

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, width*1.0/height, 1, 40)
    glMatrixMode(GL_MODELVIEW)

    C.window.width = width
    C.window.height = height

def handle_mouse(button, state, x, y):
    global C
    C.window.mouse[button] = state
    C.window.mouse_last[button] = (x, y)

    # handle scrollwheel zoom
    zfac = 1
    if button == 3:
        C.camera.distance -= zfac
        if C.camera.distance < 0:
            C.camera.distance = 0
        glutPostRedisplay()
    elif button == 4:
        C.camera.distance += zfac
        glutPostRedisplay()

def handle_motion(x, y):
    global C
    
    if C.window.mouse[GLUT_MIDDLE_BUTTON] == GLUT_DOWN:
        orig = C.window.mouse_last[GLUT_MIDDLE_BUTTON]
        delta = ((x - orig[0]) / (C.window.width * 1.0),
                 (y - orig[1]) / (C.window.height * -1.0))
        C.window.mouse_last[GLUT_MIDDLE_BUTTON] = (x, y)

        C.camera.angle -= delta[0] * 10
        C.camera.elevation -= delta[1] * 10
        limit = math.pi / 2
        if C.camera.elevation < -limit:
            C.camera.elevation = -limit
        if C.camera.elevation > limit:
            C.camera.elevation = limit
        glutPostRedisplay()

if __name__ == '__main__': main()
