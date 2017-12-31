import math


class Angle:
    def __init__(self, radians=0):
        self._radians = radians

    @classmethod
    def from_radians(cls, radians):
        return cls(radians)

    @classmethod
    def from_degrees(cls, degrees):
        return cls(degrees * (math.pi / 180.0))

    @property
    def radians(self):
        return self._radians

    @property
    def degrees(self):
        return self.radians * (180.0 / math.pi)

    def cos(self):
        return math.cos(self.radians)

    def sin(self):
        return math.sin(self.radians)

    def tan(self):
        return math.tan(self.radians)

    def __add__(self, other):
        return Angle(self.radians + other.radians)

    def __sub__(self, other):
        return Angle(self.radians - other.radians)
