import ModernGL
import glfw
import glm

from meshcheck import events


class WindowError(RuntimeError):
    pass


class Window:
    def __init__(self, size, title, gl_version):
        if not glfw.init():
            raise WindowError('glfw.init failed')

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, gl_version[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, gl_version[1])
        glfw.window_hint(glfw.DOUBLEBUFFER, True)
        self._wnd = glfw.create_window(*size, title, None, None)
        if not self._wnd:
            raise WindowError('glfw.create_window failed')
        self._init_events()

        self._ctx = None

    def _init_events(self):
        glfw.set_cursor_pos_callback(self._wnd, self._cursor_pos_callback)
        glfw.set_mouse_button_callback(self._wnd, self._mouse_button_callback)

    def _cursor_pos_callback(self, _, xpos, ypos):
        self.on_mouse_move(events.MouseMoveEvent(glm.vec2(xpos, ypos)))

    def _mouse_button_callback(self, _, button, action, mods):
        self.on_mouse_button(
            events.MouseButtonEvent(
                pos=self.get_mouse_position(),
                button=button,
                action=action,
                mods=mods))

    def get_mouse_position(self):
        return glm.vec2(*glfw.get_cursor_pos(self._wnd))

    def on_mouse_button(self, event):
        pass

    def on_mouse_move(self, event):
        pass

    def initialize(self, ctx):
        pass

    def render(self, ctx):
        pass

    def size(self):
        return glfw.get_framebuffer_size(self._wnd)

    def run(self):
        glfw.make_context_current(self._wnd)
        self._ctx = ModernGL.create_context()

        self.initialize(self._ctx)

        while not glfw.window_should_close(self._wnd):
            width, height = self.size()
            self._ctx.viewport = (0, 0, width, height)
            self.render(self._ctx)
            glfw.swap_buffers(self._wnd)
            glfw.wait_events()
