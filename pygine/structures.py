import math
from pygame import Rect
from pygine.draw import draw_rectangle
from pygine.utilities import CameraType, Color


class Quadtree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity

        self.divided = False
        self.insertion_index = 0
        self.objects = [None] * self.capacity

        self.topLeft = None
        self.topRight = None
        self.bottomRight = None
        self.bottomLeft = None

    def insert(self, pygine_object):
        if not pygine_object.bounds.colliderect(self.boundary):
            return False

        if self.insertion_index < self.capacity:
            self.objects[self.insertion_index] = pygine_object
            self.insertion_index += 1
            return True
        else:
            if not self.divided:
                self.__subdivide()

            if (
                self.topLeft.insert(pygine_object) or
                self.topRight.insert(pygine_object) or
                self.bottomRight.insert(pygine_object) or
                self.bottomLeft.insert(pygine_object)
            ):
                return True

        return False

    def query(self, area):    
        if not area.colliderect(self.boundary):
            return []

        result = []

        for i in range(len(self.objects)):
            if self.objects[i] == None:
                continue

            if area.colliderect(self.objects[i].bounds):
                result.append(self.objects[i])

        if not self.divided:
            return result

        result.extend(self.topLeft.query(area))
        result.extend(self.topRight.query(area))
        result.extend(self.bottomRight.query(area))
        result.extend(self.bottomLeft.query(area))

        return result

    def clear(self):
        if self.divided:
            self.topLeft.clear()
            self.topRight.clear()
            self.bottomRight.clear()
            self.bottomLeft.clear()

            self.topLeft = None
            self.topRight = None
            self.bottomRight = None
            self.bottomLeft = None

        self.divided = False
        self.insertion_index = 0
        self.objects = [None] * self.capacity

    def __subdivide(self):
        self.divided = True
        self.topLeft = Quadtree(
            Rect(
                self.boundary.x,
                self.boundary.y,
                self.boundary.width / 2,
                self.boundary.height / 2
            ),
            self.capacity
        )
        self.topRight = Quadtree(
            Rect(
                self.boundary.x + self.boundary.width / 2,
                self.boundary.y,
                self.boundary.width / 2,
                self.boundary.height / 2
            ),
            self.capacity
        )
        self.bottomRight = Quadtree(
            Rect(
                self.boundary.x + self.boundary.width / 2,
                self.boundary.y + self.boundary.height / 2,
                self.boundary.width / 2,
                self.boundary.height / 2
            ),
            self.capacity
        )
        self.bottomLeft = Quadtree(
            Rect(
                self.boundary.x,
                self.boundary.y + self.boundary.height / 2,
                self.boundary.width / 2,
                self.boundary.height / 2
            ),
            self.capacity
        )

    def draw(self, surface):
        draw_rectangle(
            surface,
            self.boundary,
            CameraType.DYNAMIC,
            Color.BLACK,
            1
        )

        if self.divided:
            self.topLeft.draw(surface)
            self.topRight.draw(surface)
            self.bottomRight.draw(surface)
            self.bottomLeft.draw(surface)


class Bin:
    def __init__(self, boundary, power_of_two):
        self.boundary = boundary
        self.power_of_two = power_of_two
        self.cell_size = 1 << self.power_of_two

        self.columns = int(math.ceil(float(self.boundary.width / self.power_of_two)))
        self.rows = int(math.ceil(float(self.boundary.height / self.power_of_two)))

        self.buckets = [set() for i in range(self.rows * self.columns)]

    def insert(self, pygine_object):
        if not pygine_object.bounds.colliderect(self.boundary):
            return False

        ids = self.__hash_ids(pygine_object.bounds)

        for i in ids:
            self.buckets[i].add(pygine_object)

        return len(ids) > 0

    def query(self, area):
        if not area.colliderect(self.boundary):
            return []

        result = []
        objects = set()
        ids = self.__hash_ids(area)

        for i in ids:
            for pygine_object in self.buckets[i]:
                objects.add(pygine_object)

        for pygine_object in objects:
            result.append(pygine_object)

        objects.clear()
        ids.clear()

        return result

    def clear(self):
        for i in range(len(self.buckets)):
            self.buckets[i].clear()

    def __hash_ids(self, bounds):
        result = set()
        x = -1
        y = -1
        
        if bounds.width > self.cell_size or bounds.height > self.cell_size:
            for height_offset in range(0, bounds.height, self.cell_size):
                for width_offset in range(0, bounds.width, self.cell_size):
                    x = int(bounds.x + width_offset) >> self.power_of_two
                    y = int(bounds.y + height_offset) >> self.power_of_two

                    if x < 0 or x >= self.columns or y < 0 or y >= self.rows:
                        continue

                    result.add(self.columns * y + x)

        for i in range(4):
            if i == 0:
                x = int(bounds.x) >> self.power_of_two
                y = int(bounds.y) >> self.power_of_two
            elif i == 1:
                x = int(bounds.x + bounds.width) >> self.power_of_two
                y = int(bounds.y) >> self.power_of_two
            elif i == 2:
                x = int(bounds.x + bounds.width) >> self.power_of_two
                y = int(bounds.y + bounds.height) >> self.power_of_two
            elif i == 3:
                x = int(bounds.x) >> self.power_of_two
                y = int(bounds.y + bounds.height) >> self.power_of_two

            if x < 0 or x >= self.columns or y < 0 or y >= self.rows:
                continue

            result.add(self.columns * y + x)

        return result

    def draw(self, surface):
        for y in range(self.rows):
            for x in range(self.columns):
                draw_rectangle(
                    surface,
                    Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                    CameraType.DYNAMIC,
                    Color.BLACK,
                    1
                )