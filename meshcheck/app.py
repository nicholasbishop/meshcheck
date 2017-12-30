#!/usr/bin/python

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import FTGL as ftgl
import json
import math
import numpy
import optparse
import subprocess
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
        self.font = ftgl.PolygonFont('LiberationSans-Regular.ttf')
        self.font.FaceSize(12)
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

    def __init__(self, verts, faces):
        self.verts = {}
        self.faces = {}
        for v in verts:
            self.add_vert(v, *verts[v])
        for f in faces:
            self.add_face(f, faces[f])

        # calculate bounding box
        inf = float("inf")
        bmin = [inf, inf, inf]
        bmax = [-inf, -inf, -inf]
        for v in self.verts.values():
            for axis in range(3):
                if v.co[axis] < bmin[axis]:
                    bmin[axis] = v.co[axis]
                if v.co[axis] > bmax[axis]:
                    bmax[axis] = v.co[axis]
        self.bounds = (numpy.array(bmin), numpy.array(bmax))

        # calculate a scale for the object based off widest axis
        size = self.bounds[1] - self.bounds[0]
        self.scale = -inf
        for w in size:
            if w > self.scale:
                self.scale = w
        
    def add_vert(self, name, x, y, z):
        if name in self.verts:
            raise Exception('Duplicate vertex name')
        self.verts[name] = self.Vert(name,
                                     numpy.array([x, y, z]))

    def add_face(self, name, vert_names):
        if name in self.faces:
            raise Exception('Duplicate face name')
        verts = [self.verts[v] for v in vert_names]
        
        self.faces[name] = self.Face(name, verts)


def load_json_mesh(C, text):
    json_mesh = json.loads(text)
    C.mesh = Mesh(json_mesh['verts'],
                  json_mesh['faces'])
    C.camera.distance = C.mesh.scale * 4

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
    gluPerspective(40, C.window.width*1.0/C.window.height, 0.1, 100)
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

def draw_text(text):
    # ftgl doesn't handle unicode?
    text = str(text)
    bounds = (C.font.Advance(text), C.font.line_height)
    glTranslatef(-bounds[0] / 2.0, -bounds[1] / 4.0, 0)
    C.font.Render(text)

def draw_text_3d(text, loc, scale, color):
    global C

    glDisable(GL_LIGHTING)
    glPushMatrix()
    scale *= 0.01
    glScalef(scale, scale, scale)
    glColor3fv(color)
    draw_text(text)
    glPopMatrix()
    glEnable(GL_LIGHTING)

def draw_text_2d(text, loc, color):
    global C

    ortho(0, C.window.width, 0, C.window.height)
    scale = C.prefs.vertex_text_size * 2
    glTranslatef(*loc)
    glScalef(scale, scale, 1)
    glDisable(GL_LIGHTING)
    glColor3fv(color)
    glLineWidth(2)
    draw_text(text)

def transform_to_face(f):
    # choice of Z axis here is because text will be
    # rendered on X/Y plane
    orig = numpy.array([0, 0, 1])
    new = f.no

    axis = numpy.cross(orig, new)
    dot = numpy.dot(orig, new)
    angle = math.degrees(math.acos(dot))

    glTranslatef(*f.center)

    # edge case if normal is very close to Z axis
    if dot < -0.99:
        glRotatef(180, 0, 1, 0)
    elif dot < 0.99:
        glRotatef(angle, *axis)

    # add slight offset above face
    glTranslatef(0, 0, 0.01)

def draw_axes():
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

def draw_mesh():
    global C

    perspective()

    draw_axes()

    if not C.mesh:
        return
    
    # set light position
    glEnable(GL_LIGHTING)
    glLightfv(GL_LIGHT0, GL_POSITION, C.camera.location() + [1])
    glEnable(GL_COLOR_MATERIAL)

    # draw faces
    for f in C.mesh.faces.values():
        fcol = [0.35, 0.7, 0.85, 1]
        glBegin(GL_TRIANGLES)
        glNormal3fv(f.no)
        for i in range(len(f.verts)):
            v1 = f.verts[i]
            v2 = f.verts[(i+1) % len(f.verts)]
            glColor4fv(fcol)
            glVertex3fv(v1.co)
            glVertex3fv(v2.co)
            glVertex3fv(f.center)
            fcol[0] -= 0.1
            fcol[1] -= 0.1
            fcol[2] -= 0.1
        glEnd()

        # draw normal
        glLineWidth(2)
        glColor3f(1, 0, 0)
        glBegin(GL_LINES)
        glVertex3f(*f.center)
        glVertex3f(*(f.center + f.no * C.mesh.scale / 2))
        glEnd()

        # arrow to indicate first corner and polygon direction
        glLineWidth(3)
        glPushMatrix()
        # offset slightly along normal to avoid zfighting
        glTranslatef(*(f.no * 0.001))
        glBegin(GL_LINE_STRIP)
        glColor4f(0, 0, 0, 0.5)
        # point near each corner (offset slightly along normal)
        dl = []
        for v in f.verts:
            co = f.center * 0.25 + v.co * 0.75
            dl.append(co)
            glVertex3fv(co)
        glEnd()
        # arrow head
        glBegin(GL_TRIANGLES)
        base = dl[1] * 0.05 + dl[2] * 0.95
        tip = dl[2]
        cross = numpy.cross(f.no, (tip - base))
        glVertex3fv(base - cross)
        glVertex3fv(tip)
        glVertex3fv(base + cross)
        glEnd()
        glPopMatrix()

        # label face
        glPushMatrix()
        transform_to_face(f)
        draw_text_3d(f.name, (0, 0, 0), C.mesh.scale, (0, 0, 0))
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

def get_clipboard():
    return subprocess.Popen(('xclip', '-o'), stdout=subprocess.PIPE).communicate()[0]

def handle_mouse(button, state, x, y):
    global C
    C.window.mouse[button] = state
    C.window.mouse_last[button] = (x, y)

    # handle middle-button paste
    if button == GLUT_MIDDLE_BUTTON and state == GLUT_UP:
        try:
            load_json_mesh(C, get_clipboard())
        except ValueError:
            print("Couldn't decode JSON from clipboard")
        glutPostRedisplay()

    # handle scrollwheel zoom
    zfac = 0.9
    if button == 3:
        C.camera.distance *= zfac
        if C.camera.distance < 0.1:
            C.camera.distance = 0.1
        glutPostRedisplay()
    elif button == 4:
        C.camera.distance /= zfac
        glutPostRedisplay()

def handle_motion(x, y):
    global C
    
    if C.window.mouse[GLUT_RIGHT_BUTTON] == GLUT_DOWN:
        orig = C.window.mouse_last[GLUT_RIGHT_BUTTON]
        delta = ((x - orig[0]) / (C.window.width * 1.0),
                 (y - orig[1]) / (C.window.height * -1.0))
        C.window.mouse_last[GLUT_RIGHT_BUTTON] = (x, y)

        C.camera.angle -= delta[0] * 10
        C.camera.elevation -= delta[1] * 10
        limit = math.pi / 2
        if C.camera.elevation < -limit:
            C.camera.elevation = -limit
        if C.camera.elevation > limit:
            C.camera.elevation = limit
        glutPostRedisplay()

def main():
    global C

    usage = '%prog [mesh-file]\nDisplays a mesh loaded from a JSON file.\n'
    usage += 'At runtime, press MMB to load a new mesh file from the clipboard.'
    parser = optparse.OptionParser(usage)
    (options, args) = parser.parse_args()

    if len(args):
        load_json_mesh(C, open(args[0]).read())

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

if __name__ == '__main__':
    main()
