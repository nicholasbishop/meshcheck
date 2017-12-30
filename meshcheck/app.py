import argparse
import json
import os

import attr
import ModernGL
import numpy

from meshcheck import shader, window


class MeshCheckWindow(window.Window):
    def __init__(self, mesh):
        super().__init__((1280, 1024), 'meshcheck', (3, 3))
        self._vert_vbo = None
        self._tria_vao = None
        self._quad_vao = None
        self._mesh = mesh
        self._vert_to_index = {}

    def _make_vert_vbo(self, ctx):
        lst = []
        for index, (key, value) in enumerate(self._mesh.verts.items()):
            self._vert_to_index[key] = index
            lst += value
        arr = numpy.array(lst, dtype='float32')
        return ctx.buffer(arr)

    def _make_tria_vbo(self, ctx):
        lst = []
        for tria in self._mesh.trias.values():
            for vert in tria:
                lst.append(self._vert_to_index[vert])
        arr = numpy.array(lst, dtype='uint32')
        return ctx.buffer(arr)

    def _make_tria_vao(self, ctx, prog):
        attrs = ['vert']
        fmt = ModernGL.buffers.detect_format(prog, attrs)
        vao = ctx.vertex_array(prog, [(self._vert_vbo, fmt, attrs)],
                               self._make_tria_vbo(ctx))
        return vao

    def initialize(self, ctx):
        shader_code = shader.ShaderCode.load('basic')
        prog = shader_code.create_program(ctx)

        self._vert_vbo = self._make_vert_vbo(ctx)
        self._tria_vao = self._make_tria_vao(ctx, prog)
        #self._tria_vao = ctx.simple_vertex_array(prog, , ['vert'])
        #self._quad_vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

    def render(self, ctx):
        ctx.clear(0.9, 0.9, 0.9)
        self._tria_vao.render()


@attr.s
class Mesh:
    verts = attr.ib()
    trias = attr.ib()
    quads = attr.ib()

    @classmethod
    def from_file(cls, path):
        with open(path) as rfile:
            return cls.from_json(json.load(rfile))

    @classmethod
    def from_json(cls, obj):
        verts = obj['verts']
        trias = {}
        quads = {}
        for key, val in obj['faces'].items():
            if len(val) == 3:
                trias[key] = val
            elif len(val) == 4:
                quads[key] = val
            else:
                raise NotImplementedError(
                    'only triangles and quads are allowed')
        return cls(verts=verts, trias=trias, quads=quads)


def parse_args():
    parser = argparse.ArgumentParser('simple 3D mesh visualizer')
    parser.add_argument('path', nargs='?')
    return parser.parse_args()


def run():
    args = parse_args()
    if args.path:
        mesh = Mesh.from_file(args.path)
    else:
        raise NotImplementedError('only file input works right now')
    window = MeshCheckWindow(mesh)
    window.run()
