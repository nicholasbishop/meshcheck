from meshcheck import angle

class CameraController:
    """Simple mouse camera controller."""
    def __init__(self, camera):
        self._camera = camera
        self._orig_angle = None
        self._orig_elevation = None
        self._orig_pos = None
        self._in_drag = False

    @property
    def in_drag(self):
        return self._in_drag

    def start_drag(self, pos):
        """Start camera rotation."""
        self._orig_angle = self._camera.angle
        self._orig_elevation = self._camera.elevation
        self._orig_pos = pos
        self._in_drag = True

    def update_drag(self, pos):
        """Continue camera rotation."""
        delta = pos - self._orig_pos

        dampen = 2.0

        delta_angle = angle.Angle.from_degrees(delta.x / dampen)
        delta_elevation = angle.Angle.from_degrees(delta.y / dampen)

        self._camera.angle = self._orig_angle - delta_angle
        self._camera.elevation = self._orig_elevation + delta_elevation

    def end_drag(self):
        """End camera rotation."""
        self._in_drag = False
