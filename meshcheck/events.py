import attr
import glfw


@attr.s
class MouseButtonEvent:
    pos = attr.ib()
    button = attr.ib()
    action = attr.ib()
    mods = attr.ib()

    @property
    def is_left_button(self):
        return self.button == glfw.MOUSE_BUTTON_LEFT

    @property
    def is_press(self):
        return self.action == glfw.PRESS

    @property
    def is_release(self):
        return self.action == glfw.RELEASE


@attr.s
class MouseMoveEvent:
    pos = attr.ib()
