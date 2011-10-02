#!/usr/bin/python

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import json
import pprint
import sys

_inited = False
mesh = None

class Mesh:
    def __init__(self):
        self.verts = {}
        self.faces = {}

    def add_vert(self, name, x, y, z):
        if name in self.verts:
            raise Exception('Duplicate vertex name')
        self.verts[name] = (x, y, z)

    def add_face(self, name, verts):
        if name in self.faces:
            raise Exception('Duplicate face name')
        for v in verts:
            if v not in self.verts:
                raise Exception('Unknown vertex ' + str(v))
        self.faces[name] = verts

def load_json_mesh(text):
    mesh = Mesh()
    json_mesh = json.loads(text)
    verts = json_mesh['verts']
    faces = json_mesh['faces']

    for v in verts:
        mesh.add_vert(v, *verts[v])

    for f in faces:
        mesh.add_face(f, faces[f])

    #pprint.pprint(mesh.verts)
    #pprint.pprint(mesh.faces)

    return mesh

def main():
    # get mesh
    global mesh
    mesh = load_json_mesh(open('test.json').read())

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
    color = [1.0,0.,0.,1.]
    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)

    global mesh

    for f in mesh.faces:
        glBegin(GL_POLYGON)
        for v in mesh.faces[f]:
            glVertex3fv(mesh.verts[v])
        glEnd()

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

if __name__ == '__main__': main()
