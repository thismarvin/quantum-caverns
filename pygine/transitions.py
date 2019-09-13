from enum import IntEnum
from pygine.base import PygineObject
from pygine.geometry import Circle, Rectangle
from pygine.utilities import Camera, CameraType, Color


class TransitionType(IntEnum):
    PINHOLE_OPEN = 1
    PINHOLE_CLOSE = 2
    CAGE_OPEN = 3
    CAGE_CLOSE = 4
    SLIDE = 5


class Transition(PygineObject):
    def __init__(self, speed, acceleration=0):
        super(Transition, self).__init__(Camera.BOUNDS.width / 2,
                                         Camera.BOUNDS.height / 2, Camera.BOUNDS.width, Camera.BOUNDS.height)
        self.done = False
        self.default_speed = speed
        self.speed = self.default_speed
        self.acceleration = acceleration

    def reset(self):
        raise NotImplementedError(
            "A class that inherits Transition did not implement the reset() method")

    def update(self, delta_time):
        raise NotImplementedError(
            "A class that inherits Transition did not implement the update(delta_time) method")

    def draw(self, surface):
        raise NotImplementedError(
            "A class that inherits Transition did not implement the draw(surface) method")


class Pinhole(Transition):
    def __init__(self, type):
        super(Pinhole, self).__init__(100, 250)
        self.type = type
        self.reset()

    def reset(self):
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
        #self.circle2.draw(surface, CameraType.STATIC)


class Slide(Transition):
    def __init__(self):
        super(Slide, self).__init__(1000, 5000)
        self.first_half_complete = False

        self.total = 8

        self.stagger_height = Camera.BOUNDS.height / self.total
        self.rectangle = Rectangle(
            0, 0, Camera.BOUNDS.width * 2, self.stagger_height, Color.BLACK)

        self.rectangles = [self.rectangle]
        for i in range(1, self.total):
            self.rectangles.append(
                Rectangle(
                    0,
                     self.stagger_height * i,
                      Camera.BOUNDS.width * 2,
                     self.stagger_height,
                      Color.BLACK
                )
            )

        self.reset()

    def reset(self):
        self.speed = self.default_speed
        self.done = False
        self.first_half_complete = False

        for i in range(len(self.rectangles)):
            self.rectangles[i].set_location(-self.rectangle.width - i * self.stagger_height, self.rectangles[i].y)

    def update(self, delta_time):
        if self.done:
            return

        if self.rectangle.x + self.rectangle.width > Camera.BOUNDS.width:
            self.first_half_complete = True

        if self.first_half_complete and self.rectangle.x > Camera.BOUNDS.width:
            self.rectangle.set_location(
                Camera.BOUNDS.width, self.rectangle.y)
            self.done = True

        for rectangle in self.rectangles:
            rectangle.set_location(
                rectangle.x + self.speed * delta_time, rectangle.y)

        self.speed += self.acceleration * delta_time

    def draw(self, surface):

        for rectangle in self.rectangles:
            rectangle.draw(surface, CameraType.STATIC)


class Cage(Transition):
    def __init__(self, type):
        super(Cage, self).__init__(500, 100)
        self.type = type

        self.total = 8

        self.stagger_width = Camera.BOUNDS.width / self.total

        if self.type == TransitionType.CAGE_CLOSE:
            self.rectangle = Rectangle(
                0, -Camera.BOUNDS.height * 3, self.stagger_width, Camera.BOUNDS.height * 3, Color.BLACK)

            self.rectangles = [self.rectangle]
            for i in range(1, self.total):
                self.rectangles.append(
                    Rectangle(
                        self.stagger_width * i,
                        -Camera.BOUNDS.height * 3,
                        self.stagger_width,
                        Camera.BOUNDS.height * 3,
                        Color.BLACK
                    )
                )

        elif self.type == TransitionType.CAGE_OPEN:
            self.rectangle = Rectangle(
                0, 0, self.stagger_width, Camera.BOUNDS.height * 3, Color.BLACK)

            self.rectangles = [self.rectangle]
            for i in range(1, self.total):
                self.rectangles.append(
                    Rectangle(
                        self.stagger_width * i,
                        0,
                        self.stagger_width,
                        Camera.BOUNDS.height * 3,
                        Color.BLACK
                    )
                )

        self.reset()

    def reset(self):
        self.speed = self.default_speed
        self.done = False

        for i in range(len(self.rectangles)):
            if self.type == TransitionType.CAGE_CLOSE:
                self.rectangles[i].set_location(self.rectangles[i].x, -self.rectangle.height - i * self.stagger_width)
            elif self.type == TransitionType.CAGE_OPEN:
                self.rectangles[i].set_location(self.rectangles[i].x, -i * self.stagger_width)

    def update(self, delta_time):
        if self.done:
            return

        if self.type == TransitionType.CAGE_CLOSE:
            if self.rectangle.y + Camera.BOUNDS.height > Camera.BOUNDS.height:
                self.rectangle.set_location(
                    self.rectangle.x, -64)
                self.done = True

            for rectangle in self.rectangles:
                rectangle.set_location(
                    rectangle.x, rectangle.y + self.speed * delta_time)

        elif self.type == TransitionType.CAGE_OPEN:
            if self.rectangles[len(self.rectangles) - 1].y > Camera.BOUNDS.height:
                self.done = True

            for rectangle in self.rectangles:
                rectangle.set_location(
                    rectangle.x, rectangle.y + self.speed * delta_time)

        self.speed += self.acceleration * delta_time

    def draw(self, surface):
        for rectangle in self.rectangles:
            rectangle.draw(surface, CameraType.STATIC)
