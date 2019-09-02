from enum import IntEnum
from pygine.base import PygineObject
from pygine.geometry import Circle
from pygine.utilities import Camera, CameraType, Color


class TransitionType(IntEnum):
    PINHOLE_OPEN = 1
    PINHOLE_CLOSE = 2


class Transition(PygineObject):
    def __init__(self, speed, acceleration=0):
        super(Transition, self).__init__(Camera.BOUNDS.width / 2,
                                         Camera.BOUNDS.height / 2, Camera.BOUNDS.width, Camera.BOUNDS.height)
        self.done = False
        self.default_speed = speed
        self.speed = self.default_speed
        self.acceleration = acceleration

    def _reset(self):
        raise NotImplementedError(
            "A class that inherits Transition did not implement the reset() method")

    def _update(self, delta_time):
        raise NotImplementedError(
            "A class that inherits Transition did not implement the update(delta_time) method")

    def _draw(self, surface):
        raise NotImplementedError(
            "A class that inherits Transition did not implement the draw(surface) method")


class Pinhole(Transition):
    def __init__(self, type):
        super(Pinhole, self).__init__(100, 250)
        self.type = type
        self._reset()

    def _reset(self):
        self.speed = self.default_speed
        self.done = False
        greater_camera_dimesion = Camera.BOUNDS.width if Camera.BOUNDS.width > Camera.BOUNDS.height else Camera.BOUNDS.height
        if self.type == TransitionType.PINHOLE_OPEN:
            self.circle = Circle(
                self.x,
                self.y,
                greater_camera_dimesion * 0.75,
                Color.BLACK,
                greater_camera_dimesion * 0.75 - 1
            )
            self.circle2 = Circle(
                self.x,
                self.y - 1,
                greater_camera_dimesion * 0.75,
                Color.BLACK,
                greater_camera_dimesion * 0.75 - 1
            )
        if self.type == TransitionType.PINHOLE_CLOSE:
            self.circle = Circle(
                self.x,
                self.y,
                greater_camera_dimesion * 0.75,
                Color.BLACK,
                1
            )
            self.circle2 = Circle(
                self.x,
                self.y - 1,
                greater_camera_dimesion * 0.75,
                Color.BLACK,
                1
            )

    def update(self, delta_time):
        if self.done:
            return

        if self.type == TransitionType.PINHOLE_OPEN:
            if self.circle.thickness > 10:
                self.circle.set_thickness(
                    self.circle.thickness - self.speed * delta_time)
                self.circle2.set_thickness(self.circle.thickness)
            else:
                self.circle.set_thickness(10)
                self.circle2.set_thickness(self.circle.thickness)
                self.done = True
        if self.type == TransitionType.PINHOLE_CLOSE:
            if self.circle.thickness < self.circle.radius:
                self.circle.set_thickness(
                    self.circle.thickness + self.speed * delta_time)
                self.circle2.set_thickness(self.circle.thickness)
            else:
                self.circle.set_thickness(0)
                self.circle2.set_thickness(self.circle.thickness)
                self.done = True

        self.speed += self.acceleration * delta_time

    def draw(self, surface):
        self.circle.draw(surface, CameraType.STATIC)
        self.circle2.draw(surface, CameraType.STATIC)
