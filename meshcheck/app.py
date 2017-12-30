import struct

from meshcheck import window

class MeshCheckWindow(window.Window):
    def __init__(self):
        super().__init__((1280, 1024), 'meshcheck', (3, 3))
        self._vao = None

    def initialize(self, ctx):
        prog = ctx.program([
            ctx.vertex_shader('''
                #version 330
                in vec2 vert;
                void main() {
                        gl_Position = vec4(vert, 0.0, 1.0);
                }
        '''),
            ctx.fragment_shader('''
                #version 330
                out vec4 color;
                void main() {
                        color = vec4(0.3, 0.5, 1.0, 1.0);
                }
        '''),
        ])
        vbo = ctx.buffer(struct.pack('6f', 0.0, 0.8, -0.6, -0.8, 0.6, -0.8))
        self._vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

    def render(self, ctx):
        ctx.clear(0.9, 0.9, 0.9)
        self._vao.render()


def run():
    window = MeshCheckWindow()
    window.run()
