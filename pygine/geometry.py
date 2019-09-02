from pygame import Rect
from pygine.base import PygineObject
from pygine.draw import draw_rectangle, draw_circle
from pygine.utilities import CameraType, Color


class Shape(PygineObject):
    def __init__(self, x, y, width, height, color):
        super(Shape, self).__init__(x, y, width, height)
        self.color = color
        self.thickness = 0

    def set_thickness(self, thickness):
        raise NotImplementedError(
            "A class that inherits Shape did not implement the set_thickness(thickness) method")

    def draw(self, surface, camera_type=CameraType.DYNAMIC):
        raise NotImplementedError(
            "A class that inherits Shape did not implement the draw(surface) method")


class Rectangle(Shape):
    def __init__(self, x, y, width, height, color=Color.WHITE, thickness=0):
        super(Rectangle, self).__init__(x, y, width, height, color)
        self.set_thickness(thickness)
        self.reset()

    def reset(self):
        if self.thickness == 0:
            self.rectangles = [self.bounds]
        else:
            self.rectangles = [
                # Top
                Rect(
                    self.x,
                    self.y,
                    self.width,
                    self.thickness
                ),
                # Right
                Rect(
                    self.x + self.width - self.thickness,
                    self.y + self.thickness,
                    self.thickness,
                    self.height - self.thickness * 2
                ),
                # Bottom
                Rect(
                    self.x,
                    self.y + self.height - self.thickness,
                    self.width,
                    self.thickness
                ),
                # Left
                Rect(
                    self.x,
                    self.y + self.thickness,
                    self.thickness,
                    self.height - self.thickness * 2
                ),
            ]

    def set_location(self, x, y):
        super(Rectangle, self).set_location(x, y)
        self.reset()

    def set_thickness(self, thickness):
        self.thickness = thickness
        if self.thickness < 0:
            self.thickness = 0

    def draw(self, surface, camera_type=CameraType.DYNAMIC):
        for r in self.rectangles:
            draw_rectangle(
                surface,
                r,
                camera_type,
                self.color
            )


class Circle(Shape):
    def __init__(self, x, y, radius, color=Color.WHITE, thickness=0):
        super(Circle, self).__init__(x, y, radius, radius, color)
        self.radius = radius
        self.set_thickness(thickness)

    def set_thickness(self, thickness):
        self.thickness = thickness
        if self.thickness < 0:
            self.thickness = 1
        if self.thickness > self.radius:
            self.thickness = self.radius

    def draw(self, surface, camera_type=CameraType.DYNAMIC):
        draw_circle(
            surface,
            self.location,
            self.radius,
            camera_type,
            self.color,
            self.thickness
        )
