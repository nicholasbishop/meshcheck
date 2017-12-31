import math

import cairo
import glm
import numpy

import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo

from meshcheck import shader, util

def create_layout(cairo_ctx, text):
    layout = PangoCairo.create_layout(cairo_ctx)
    layout.set_font_description(Pango.FontDescription('serif 24'))
    auto_length = -1
    layout.set_text(text, auto_length)
    return layout


def measure_text(text):
    surface_size = (1, 1)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *surface_size)
    cairo_ctx = cairo.Context(surface)
    layout = create_layout(cairo_ctx, text)

    width, height = layout.get_size()
    scale = Pango.SCALE
    return (math.ceil(width / scale), math.ceil(height / scale))


def render(text):
    width, height = measure_text(text)
    surface = cairo.ImageSurface(cairo.FORMAT_A8, width, height)
    ctx = cairo.Context(surface)

    # Black text on white background
    ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0);
    ctx.paint()

    # Override the alpha channel
    ctx.set_operator(cairo.OPERATOR_SOURCE);
    ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0);

    layout = create_layout(ctx, text)
    PangoCairo.show_layout(ctx, layout)

    return surface


class TextNode:
    Program = None

    def __init__(self, ctx, vert):
        self._text = vert[0]
        self._where = vert[1]

        if TextNode.Program is None:
            shader_code = shader.ShaderCode.load('text')
            TextNode.Program = shader_code.create_program(ctx)

        self._vbo = self._make_vert_vbo(ctx)
        self._vao = self._make_tria_vao(ctx)
        self._texture = self._make_texture(ctx)

        TextNode.Program.uniforms['size'].value = self._texture.size

    @staticmethod
    def _make_vert_vbo(ctx):
        # Format: Two triangles with 2d position and 2d UV coord
        # yapf: disable
        arr = numpy.array([
            0, 0, 0, 1,
            1, 0, 1, 1,
            1, 1, 1, 0,
            0, 0, 0, 1,
            1, 1, 1, 0,
            0, 1, 0, 0
        ], dtype='float32')
        # yapf: enable
        return ctx.buffer(arr)

    def _make_tria_vao(self, ctx):
        attrs = ['pos', 'uv']
        return ctx.simple_vertex_array(self.Program, self._vbo, attrs)

    def _make_texture(self, ctx):
        surface = render(self._text)
        components = 1
        stride = surface.get_stride()
        width = surface.get_width()
        height = surface.get_height()
        # Remove the pixel data that comes from |stride|, ModernGL
        # doesn't have an input stride parameter currently
        src_data = surface.get_data()
        dst_data = bytes()
        for row in range(height):
            dst_data += src_data[row * stride:row * stride + width * components]
        return ctx.texture((width, height), components, dst_data)

    def render(self, proj, model_view):
        model_view = glm.translate(model_view, self._where)
        self.Program.uniforms['model_view'].write(util.to_gl(model_view))
        self.Program.uniforms['proj'].write(util.to_gl(proj))
        #self._sampler = self._texture
        self._texture.use()
        self._vao.render()
