import argparse
import json
import sys

import attr
import ModernGL
import numpy

from meshcheck import (camera, camera_controller, shader, text_render, util,
                       window)


class MeshCheckWindow(window.Window):
    def __init__(self, mesh):
        super().__init__((1280, 1024), 'meshcheck', (3, 3))
        self._vert_vbo = None
        self._tria_vao = None
        self._mesh = mesh
        self._vert_to_index = {}
        self._prog = None
        self._text_nodes = None
        self._mvp = None
        self._camera = camera.Camera()
        self._camera_controller = camera_controller.CameraController(
            self._camera)

    def _make_vert_vbo(self, ctx):
        lst = []
        for index, (key, value) in enumerate(self._mesh.verts.items()):
            self._vert_to_index[key] = index
            lst += value
        arr = numpy.array(lst, dtype='float32')
        return ctx.buffer(arr)

    def _make_tria_vbo(self, ctx):
        lst = []
        for tria in self._mesh.faces.values():
            # Naive triangle tessellation
            for index in range(2, len(tria)):
                for offset in (0, index - 1, index):
                    lst.append(self._vert_to_index[tria[offset]])

        arr = numpy.array(lst, dtype='uint32')
        return ctx.buffer(arr)

    def _make_tria_vao(self, ctx, prog):
        attrs = ['pos']
        fmt = ModernGL.buffers.detect_format(prog, attrs)
        vao = ctx.vertex_array(prog, [(self._vert_vbo, fmt, attrs)],
                               self._make_tria_vbo(ctx))
        return vao

    def on_mouse_button(self, event):
        if event.is_left_button:
            if event.is_press:
                self._camera_controller.start_drag(event.pos)
            elif event.is_release:
                self._camera_controller.end_drag()

    def on_mouse_move(self, event):
        if self._camera_controller.in_drag:
            self._camera_controller.update_drag(event.pos)

    def initialize(self, ctx):
        shader_code = shader.ShaderCode.load('default')
        self._prog = shader_code.create_program(ctx)
        self._mvp = self._prog.uniforms['mvp']

        self._text_nodes = [
            text_render.TextNode(ctx, vert)
            for vert in self._mesh.verts.items()
        ]

        self._vert_vbo = self._make_vert_vbo(ctx)
        self._tria_vao = self._make_tria_vao(ctx, self._prog)

    def render(self, ctx):
        ctx.clear(0.9, 0.9, 0.9)
        ctx.enable(ModernGL.DEPTH_TEST)
        ctx.disable(ModernGL.CULL_FACE)
        self._camera.size = self.size()
        self._mvp.write(util.to_gl(self._camera.mvp))
        self._tria_vao.render()
        for text_node in self._text_nodes:
            text_node.render(self._camera.proj, self._camera.model_view)


@attr.s
class Mesh:
    verts = attr.ib()
    faces = attr.ib()

    @classmethod
    def from_file(cls, path):
        with open(path) as rfile:
            return cls.from_json(json.load(rfile))

    @classmethod
    def from_stdin(cls):
        return cls.from_json(json.load(sys.stdin))

    @classmethod
    def from_json(cls, obj):
        return cls(verts=obj['verts'], faces=obj['faces'])


def parse_args():
    parser = argparse.ArgumentParser('simple 3D mesh visualizer')
    parser.add_argument('path', nargs='?')
    return parser.parse_args()


def run():
    args = parse_args()
    if args.path:
        mesh = Mesh.from_file(args.path)
    else:
        print('reading from stdin...')
        mesh = Mesh.from_stdin()
    wnd = MeshCheckWindow(mesh)
    wnd.run()
