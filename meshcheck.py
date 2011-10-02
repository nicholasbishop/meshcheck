#!/usr/bin/python

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import json
import math
import numpy
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

    class Preferences:
        def __init__(self):
            self.vertex_text_size = 1

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
        self.prefs = self.Preferences()
        self.window = self.Window()

C = Context()

class Mesh:
    def __init__(self):
        self.verts = {}
        self.faces = {}

    def add_vert(self, name, x, y, z):
        if name in self.verts:
            raise Exception('Duplicate vertex name')
        self.verts[name] = numpy.array([x*1.0, y*1.0, z*1.0])

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
        n = numpy.cross(v1, v2)
        return n * (1.0 / numpy.linalg.norm(n))

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

def ortho(left, right, top, bottom):
    # set up ortho view
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left, right, top, bottom)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def perspective():
    global C
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, C.window.width*1.0/C.window.height, 1, 40)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    eye = C.camera.location()
    gluLookAt(eye[0], eye[1], eye[2],
              0,0,0,
              0,1,0)

def draw_background(top_color, bottom_color):
    '''
    Clear color/depth and draw a background quad.
    '''
    # clear color and depth, disable lighting
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glDisable(GL_LIGHTING)

    ortho(0, 1, 0, 1)

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

def draw_text_3d(text, loc, color):
    glDisable(GL_LIGHTING)
    glPushMatrix()
    scale = 0.001
    glScalef(scale, scale, scale)
    glColor3fv(color)
    glLineWidth(2)
    for c in text:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(c))
    glPopMatrix()
    glEnable(GL_LIGHTING)

def draw_text_2d(text, loc, color):
    global C

    ortho(0, C.window.width, 0, C.window.height)
    scale = C.prefs.vertex_text_size * 0.2
    glTranslatef(*loc)
    glScalef(scale, scale, 1)
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glLineWidth(2)
    for c in text:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(c))

def transform_to_face(mesh, f):
    # find center
    center = numpy.array((0, 0, 0))
    for v in mesh.faces[f]:
        center += mesh.verts[v]
    center = center * (1.0 / len(mesh.faces[f]))

    # find orientation
    n = C.mesh.face_normal(f)
    w = numpy.array([0, 0, 1])
    axis = numpy.cross(n, w)
    angle = -math.degrees(math.acos(numpy.dot(n, w))) + 180
    #print f, angle, axis

    glTranslatef(*center)
    glRotatef(angle, *axis)

    # add slight offset above face
    glTranslatef(0, 0, 0.001)

def draw_mesh():
    global C

    perspective()

    # draw axes
    big = 1000
    glLineWidth(1)
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(big, 0, 0)

    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, big, 0)

    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, big)
    glEnd()

    # set light position
    glEnable(GL_LIGHTING)
    glLightfv(GL_LIGHT0, GL_POSITION, -C.camera.location() + [1])

    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.35, 0.7, 0.85, 1])
    #glMaterialfv(GL_FRONT, GL_DIFFUSE, [1, 0, 0, 1])

    # draw faces
    for f in C.mesh.faces:
        glBegin(GL_POLYGON)
        glNormal3fv(C.mesh.face_normal(f))
        for v in C.mesh.faces[f]:
            glVertex3fv(C.mesh.verts[v])
        glEnd()

        # label face
        glPushMatrix()
        transform_to_face(C.mesh, f)
        draw_text_3d(f, (0, 0, 0), (0, 0, 0))
        glPopMatrix()

    # label vertices
    for v in C.mesh.verts:
        draw_text_2d(v,
                     gluProject(*C.mesh.verts[v]),
                     (0, 0, 0))
        perspective()

def init_state():
    global C
    if not C.inited:
        C.inited = True
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
  

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
