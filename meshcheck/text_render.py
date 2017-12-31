import math

import cairo

import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo


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
