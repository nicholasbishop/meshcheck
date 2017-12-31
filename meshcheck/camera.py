"""View/camera math."""

import math

import numpy
import glm

from meshcheck import angle


class Camera:
    """Simple angle-elevation camera."""

    def __init__(self):
        self._elevation = angle.Angle()
        self._angle = angle.Angle()
        self._distance = 5
        self._size = (1, 1)
        self._model_view = None
        self._proj = None
        self._mvp = None
        self._update()

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, val):
        self._angle = val
        self._update()

    @property
    def elevation(self):
        return self._elevation

    @elevation.setter
    def elevation(self, val):
        self._elevation = val
        self._update()

    @property
    def mvp(self):
        """Model-view-projection matrix."""
        return self._mvp

    def aspect_ratio(self):
        height = self._size[1]
        if height == 0:
            return 1
        else:
            return self._size[0] / height

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, val):
        self._size = val
        self._update()

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, val):
        self._distance = val
        self._update()

    def _update(self):
        eye = numpy.array((self.angle.sin(), self.elevation.sin(),
                           self.angle.cos()))
        eye = eye * self.distance / numpy.linalg.norm(eye)

        target = (0, 0, 0)
        up = (0, 1, 0)
        self._model_view = glm.lookAt(eye, target, up)

        fovy = 70.0 * (math.pi / 180.0)
        aspect = self.aspect_ratio()
        near = 0.1
        far = 100.0
        self._proj = glm.perspective(fovy, aspect, near, far)

        self._mvp = self._proj * self._model_view

