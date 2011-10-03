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
    class Vert:
        def __init__(self, name, co):
            self.name = name
            self.co = co

    class Face:
        def __init__(self, name, verts):
            self.name = name
            self.verts = verts
            
            # calculate normal, assuming triangle for now
            v1 = verts[1].co - verts[0].co
            v2 = verts[1].co - verts[2].co
            no = numpy.cross(v2, v1)
            self.no = no * (1.0 / numpy.linalg.norm(no))

            # calculate center
            self.center = numpy.average([v.co for v in verts], 0)

    def __init__(self):
        self.verts = {}
        self.faces = {}

    def add_vert(self, name, x, y, z):
        if name in self.verts:
            raise Exception('Duplicate vertex name')
        self.verts[name] = self.Vert(name,
                                     numpy.array([x, y, z]))
        # TODO
        self.verts[name].co *= 4

    def add_face(self, name, vert_names):
        if name in self.faces:
            raise Exception('Duplicate face name')
        verts = [self.verts[v] for v in vert_names]
        
        self.faces[name] = self.Face(name, verts)


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
    C.mesh = load_json_mesh(open('test01.json').read())

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

# not really correct obviously, but this at least gets close
def transform_to_face(f):
    # find orientation
    w = numpy.array([0, 0, 1])
    dot = numpy.dot(f.no, w)
    changed = False
    if abs(dot) < 0.01 or abs(dot) > 0.99:
        w = numpy.array([0, 1, 0])
        dot = numpy.dot(f.no, w)
        changed = True

    axis = numpy.cross(w, f.no)
    angle = math.degrees(math.acos(dot))

    glTranslatef(*f.center)
    glRotatef(angle, *axis)
    if changed:
        glRotatef(90, -1, 0, 0)

    # add slight offset above face
    glTranslatef(0, 0, 0.01)

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
    glLightfv(GL_LIGHT0, GL_POSITION, C.camera.location() + [1])
    glEnable(GL_COLOR_MATERIAL)

    # draw faces
    for f in C.mesh.faces.values():
        glColor4f(0.35, 0.7, 0.85, 0.5)
        glBegin(GL_POLYGON)
        glNormal3fv(f.no)
        for v in f.verts:
            glVertex3fv(v.co)
        glEnd()

        # draw normal
        glLineWidth(2)
        glColor3f(1, 0, 0)
        glBegin(GL_LINES)
        glVertex3f(*f.center)
        glVertex3f(*(f.center + f.no))
        glEnd()

        # label face
        glPushMatrix()
        transform_to_face(f)
        draw_text_3d(f.name, (0, 0, 0), (0, 0, 0))
        glPopMatrix()

    # label vertices
    for v in C.mesh.verts.values():
        draw_text_2d(v.name,
                     gluProject(*v.co),
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
