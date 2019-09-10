import math


class Vector2:
    "a poor man's vector class."

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    @staticmethod
    def distance_between(vector_a, vector_b):
        return math.sqrt((vector_a.x - vector_b.x)**2 + (vector_a.y - vector_b.y)**2)

    def length(self):
        "Returns the length of this vector."
        return math.sqrt(self.x**2 + self.y**2)

    def add(self, value):
        if isinstance(value, Vector2):
            self.x += value.x
            self.y += value.y
        else:
            self.x += value
            self.y += value
            
    def subtract(self, value):
        if isinstance(value, Vector2):
            self.x -= value.x
            self.y -= value.y
        else:
            self.x -= value
            self.y -= value

    def multiply(self, value):
        if isinstance(value, Vector2):
            self.x *= value.x
            self.y *= value.y
        else:
            self.x *= value
            self.y *= value

    def divide(self, value):
        if isinstance(value, Vector2):
            self.x /= value.x
            self.y /= value.y
        else:
            self.x /= value
            self.y /= value

    def normalize(self):
        "Converts this vector into a unit vector."
        magnitude = self.length()
        if magnitude > 0:
            self.divide(magnitude)

    def set_magnitude(self, magnitude):
        "Set the length of the vector to magnitude."
        self.normalize()
        self.x *= magnitude
        self.y *= magnitude

    def limit(self, max_force):
        "Limit the length of the vector to max_force."
        if self.length() ** 2 > max_force ** 2:
            self.normalize()
            self.set_magnitude(max_force)

    def lerp(self, target, amount):
        "A linear interpolation between this vector and target vector by a given amount."
        self.x = (1 - amount) * self.x + amount * target.x
        self.y = (1 - amount) * self.y + amount * target.y