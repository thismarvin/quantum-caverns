from pygame import Rect
from pygine.maths import Vector2


class PygineObject(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.location = Vector2(self.x, self.y)
        self.bounds = Rect(self.x, self.y, self.width, self.height)

    def set_width(self, width):
        self.width = width
        self.bounds = Rect(self.x, self.y, self.width, self.height)

    def set_height(self, height):
        self.height = height
        self.bounds = Rect(self.x, self.y, self.width, self.height)

    def set_location(self, x, y):
        self.x = x
        self.y = y
        self.location = Vector2(self.x, self.y)
        self.bounds = Rect(self.x, self.y, self.width, self.height)
