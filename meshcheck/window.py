import ModernGL
import glfw

GLFW_INITIALIZED = False


class WindowError(RuntimeError):
    pass


def initialize_glfw():
    """Initialize the library if not already initialized."""
    if not glfw.init():
        raise WindowError('glfw.init failed')
    global GLFW_INITIALIZED
    GLFW_INITIALIZED = True


class Window:
    def __init__(self, size, title, gl_version):
        initialize_glfw()

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, gl_version[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, gl_version[1])
        self._wnd = glfw.create_window(*size, title, None, None)
        if not self._wnd:
            raise WindowError('glfw.create_window failed')

        self._ctx = None

    def initialize(self, ctx):
        pass

    def render(self, ctx):
        pass

    def run(self):
        glfw.make_context_current(self._wnd)
        self._ctx = ModernGL.create_context()

        self.initialize(self._ctx)

        while not glfw.window_should_close(self._wnd):
            width, height = glfw.get_framebuffer_size(self._wnd)
            self._ctx.viewport = (0, 0, width, height)
            self.render(self._ctx)
            glfw.swap_buffers(self._wnd)
            glfw.wait_events()
