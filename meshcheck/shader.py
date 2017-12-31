"""Shader-related utilities."""

import os

import attr


class ShaderError(RuntimeError):
    """Shader-related exception."""
    pass


# pylint can't find __slots__
#
# pylint: disable=no-member


@attr.s(frozen=True, slots=True)
class ShaderCode:
    """Shader code loader."""
    vert = attr.ib(default=None)
    geom = attr.ib(default=None)
    frag = attr.ib(default=None)

    @classmethod
    def load(cls, base_name):
        """Load a group of shaders from ./shaders/<base_name>.<kind>.glsl."""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        shader_dir = os.path.join(script_dir, 'shaders')
        shader_dir = os.path.relpath(shader_dir)
        base_path = os.path.join(shader_dir, base_name)
        codes = cls(
            **{kind: cls._load_one(base_path, kind)
               for kind in cls.__slots__})
        if not codes.vert:
            raise ShaderError('vert shader is required')
        if not codes.vert:
            raise ShaderError('frag shader is required')
        return codes

    @staticmethod
    def _load_one(base_path, kind):
        try:
            path = '{}.{}.glsl'.format(base_path, kind)
            with open(path) as rfile:
                print('loading {}'.format(path))
                return rfile.read()
        except IOError:
            return None

    def create_shader(self, ctx, kind):
        """Create a ModernGL shader."""
        funcs = {
            'vert': 'vertex_shader',
            'frag': 'fragment_shader',
            'geom': 'geometry_shader',
        }
        func = getattr(ctx, funcs[kind])
        code = getattr(self, kind)
        return func(code)

    def has_shader(self, kind):
        """Check if shader code of type |kind| is loaded."""
        return getattr(self, kind) is not None

    def create_program(self, ctx):
        """Create a ModernGL shader program."""
        shaders = [
            self.create_shader(ctx, kind) for kind in self.__slots__
            if self.has_shader(kind)
        ]
        return ctx.program(shaders)
