class Camera:
    def __init__(self):
        self.elevation = 0
        self.angle = 0
        self.distance = 5

    def location(self):
        l = numpy.array((math.sin(self.angle), math.sin(self.elevation),
                         math.cos(self.angle)))
        return l * self.distance / numpy.linalg.norm(l)
