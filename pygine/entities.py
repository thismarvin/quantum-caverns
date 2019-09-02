from enum import IntEnum
import math
from pygame import Rect
from pygine.base import PygineObject
from pygine.draw import draw_rectangle
from pygine.geometry import Rectangle, Circle
from pygine import globals
from pygine.input import InputType, pressed, pressing
from pygine.maths import Vector2
from pygine.resource import Sprite, SpriteType
from pygine.utilities import CameraType, Color
from random import randint


class Entity(PygineObject):
    def __init__(self, x=0, y=0, width=1, height=1):
        super(Entity, self).__init__(x, y, width, height)
        self.color = Color.WHITE
        self.layer = 0
        self.remove = False
        self.__bounds_that_actually_draw_correctly = Rectangle(
            self.x, self.y, self.width, self.height, self.color, 2)

    def set_color(self, color):
        self.color = color
        self.__bounds_that_actually_draw_correctly.color = color

    def set_location(self, x, y):
        super(Entity, self).set_location(x, y)
        self.__bounds_that_actually_draw_correctly.set_location(self.x, self.y)

    def update(self, delta_time, scene_data):
        raise NotImplementedError(
            "A class that inherits Entity did not implement the update(delta_time, scene_data) method")

    def _draw_bounds(self, surface, camera_type):
        self.__bounds_that_actually_draw_correctly.draw(surface, camera_type)

    def draw(self, surface):
        raise NotImplementedError(
            "A class that inherits Entity did not implement the draw(surface) method")


class Direction(IntEnum):
    NONE = 0,
    UP = 1,
    DOWN = 2,
    LEFT = 3,
    RIGHT = 4


class Kinetic(Entity):
    def __init__(self, x, y, width, height, speed):
        super(Kinetic, self).__init__(x, y, width, height)
        self.velocity = Vector2()
        self.default_move_speed = speed
        self.move_speed = 0
        self.facing = Direction.NONE
        self.collision_rectangles = []
        self.collision_width = 0

    def _update_collision_rectangles(self):
        self.collision_width = 2
        self.collision_rectangles = [
            Rect(self.x + self.collision_width, self.y - self.collision_width,
                 self.width - self.collision_width * 2, self.collision_width),
            Rect(self.x + self.collision_width, self.y + self.height, self.width -
                 self.collision_width * 2, self.collision_width),
            Rect(self.x - self.collision_width, self.y + self.collision_width,
                 self.collision_width, self.height - self.collision_width * 2),
            Rect(self.x + self.width, self.y + self.collision_width,
                 self.collision_width, self.height - self.collision_width * 2)
        ]

    def _calculate_scaled_speed(self, delta_time):
        self.move_speed = self.default_move_speed * delta_time

    def _apply_force(self, delta_time):
        raise NotImplementedError(
            "A class that inherits Kinetic did not implement the _apply_force(delta_time) method")

    def _collision(self, scene_data):
        raise NotImplementedError(
            "A class that inherits Kinetic did not implement the _collision(entities, entity_quad_tree) method")

    def update(self, delta_time, scene_data):
        raise NotImplementedError(
            "A class that inherits Kinetic did not implement the update(delta_time, scene_data) method")

    def _draw_collision_rectangles(self, surface):
        for r in self.collision_rectangles:
            draw_rectangle(
                surface,
                r,
                CameraType.DYNAMIC,
                Color.RED,
            )


class Actor(Kinetic):
    def __init__(self, x, y, width, height, speed):
        super(Actor, self).__init__(x, y, width, height, speed)

    def _update_input(self):
        raise NotImplementedError(
            "A class that inherits Actor did not implement the _update_input() method")


class Player(Actor):
    def __init__(self, x, y):
        super(Player, self).__init__(x, y, 14, 8, 50)
        self.sprite = Sprite(self.x - 9, self.y - 24, SpriteType.PLAYER)
        self.query_result = None

    def set_location(self, x, y):
        super(Player, self).set_location(x, y)
        self.sprite.set_location(self.x - 9, self.y - 24)

    def _apply_force(self, delta_time):
        self.set_location(self.x + self.velocity.x, self.y + self.velocity.y)

    def _update_input(self):
        if pressing(InputType.UP) and not pressing(InputType.DOWN):
            self.velocity.y = -1 * self.move_speed

        if pressing(InputType.DOWN) and not pressing(InputType.UP):
            self.velocity.y = 1 * self.move_speed

        if not pressing(InputType.UP) and not pressing(InputType.DOWN):
            self.velocity.y = 0

        if pressing(InputType.LEFT) and not pressing(InputType.RIGHT):
            self.velocity.x = -1 * self.move_speed

        if pressing(InputType.RIGHT) and not pressing(InputType.LEFT):
            self.velocity.x = 1 * self.move_speed

        if not pressing(InputType.LEFT) and not pressing(InputType.RIGHT):
            self.velocity.x = 0

    def __rectanlge_collision_logic(self, entity):
        # Bottom
        if self.collision_rectangles[0].colliderect(entity.bounds) and self.velocity.y < 0:
            self.set_location(self.x, entity.bounds.bottom)
        # Top
        if self.collision_rectangles[1].colliderect(entity.bounds) and self.velocity.y > 0:
            self.set_location(self.x, entity.bounds.top - self.bounds.height)
        # Right
        if self.collision_rectangles[2].colliderect(entity.bounds) and self.velocity.x < 0:
            self.set_location(entity.bounds.right, self.y)
        # Left
        if self.collision_rectangles[3].colliderect(entity.bounds) and self.velocity.x > 0:
            self.set_location(entity.bounds.left - self.bounds.width, self.y)

    def _collision(self, scene_data):
        if (globals.debugging):
            for e in scene_data.entities:
                e.set_color(Color.WHITE)

        self.area = Rect(
           self.x - 52,
           self.y - 16,
           self.width + 52 * 2,
           self.height + 16 * 2
        )

        self.query_result = scene_data.entity_quad_tree.query(self.area)
        for e in self.query_result:
            if e is self:
                continue

            if (globals.debugging):
                e.set_color(Color.RED)

            if isinstance(e, Block):
                self.__rectanlge_collision_logic(e)
                self._update_collision_rectangles()

    def update(self, delta_time, scene_data):
        self._calculate_scaled_speed(delta_time)
        self._update_input()
        self._apply_force(delta_time)
        self._update_collision_rectangles()
        self._collision(scene_data)

    def draw(self, surface):
        if globals.debugging:
            self._draw_collision_rectangles(surface)
            draw_rectangle(
                surface,
                self.bounds,
                CameraType.DYNAMIC,
                self.color
            )
            draw_rectangle(
                surface,
                self.area,
                CameraType.DYNAMIC,
                Color.BLACK,
                1
            )
        else:
            self.sprite.draw(surface, CameraType.DYNAMIC)


class Block(Entity):
    def __init__(self, x, y):
        super(Block, self).__init__(x, y, 52, 16)
        self.sprite = Sprite(self.x - 6, self.y - 13, SpriteType.BLOCK)

    def update(self, delta_time, scene_data):
        pass

    def draw(self, surface):
        if globals.debugging:
            draw_rectangle(surface, self.bounds,
                           CameraType.DYNAMIC, self.color)
        else:
            self.sprite.draw(surface, CameraType.DYNAMIC)


class Boid(Kinetic):
    def __init__(self, x, y):
        super(Boid, self).__init__(x, y, 8, 8, 50)
        self.circle = Circle(self.x, self.y, self.width / 2, Color.WHITE, 1)

        self.steer = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.velocity = Vector2(
            -self.default_move_speed +
            randint(0, 5) * self.default_move_speed * 2 / 5,
            -self.default_move_speed +
            randint(0, 5) * self.default_move_speed * 2 / 5,
        )

        self.max_force = 0.5
        self.view_radius = 16

        self.query_result = None

    def set_location(self, x, y):
        super(Boid, self).set_location(x, y)
        self.circle.set_location(
            self.x - self.width / 2, self.y - self.width / 2)

    def _apply_force(self, delta_time):
        self.velocity = Vector2(
            self.velocity.x + self.steer.x,
            self.velocity.y + self.steer.y
        )

        self.set_location(self.x + self.velocity.x * delta_time,
                          self.y + self.velocity.y * delta_time)

    def _collision(self, scene_data):
        if self.x < -self.width:
            self.set_location(scene_data.scene_bounds.width + self.width, self.y)
        if self.x > scene_data.scene_bounds.width + self.width:
            self.set_location(-self.width, self.y)
        if self.y < -self.height:
            self.set_location(self.x, scene_data.scene_bounds.height + self.height)
        if self.y > scene_data.scene_bounds.height + self.height:
            self.set_location(self.x, -self.height)

    def __separation(self):
        steer = Vector2(0, 0)
        cumulative = Vector2(0, 0)
        force = Vector2(0, 0)
        distance = 0
        total = 0

        for e in self.query_result:
            if e is self:
                continue

            distance = Vector2.distance_between(e.location, self.location)
            if distance > 0 and distance < self.width:
                force = Vector2(
                    self.location.x - e.location.x,
                    self.location.y - e.location.y
                )
                force.divide(distance**2)
                cumulative.add(force)
                total += 1

        if total > 0:
            cumulative.divide(total)
            cumulative.set_magnitude(self.default_move_speed)

            steer = Vector2(
                cumulative.x - self.velocity.x,
                cumulative.y - self.velocity.y
            )
            steer.limit(self.max_force)

        return steer

    def __alignment(self):
        steer = Vector2(0, 0)
        cumulative = Vector2(0, 0)
        distance = 0
        total = 0

        for e in self.query_result:
            if e is self:
                continue

            if isinstance(e, Boid):
                distance = Vector2.distance_between(e.location, self.location)
                if distance > 0 and distance < self.view_radius:
                    cumulative.add(e.velocity)
                    total += 1

        if total > 0:
            cumulative.divide(total)
            cumulative.set_magnitude(self.default_move_speed)

            steer = Vector2(
                cumulative.x - self.velocity.x,
                cumulative.y - self.velocity.y
            )
            steer.limit(self.max_force)

        return steer

    def __cohesion(self):
        steer = Vector2(0, 0)
        cumulative = Vector2(0, 0)
        distance = 0
        total = 0

        for e in self.query_result:
            if e is self:
                continue

            distance = Vector2.distance_between(e.location, self.location)
            if distance > 0 and distance < self.view_radius:
                cumulative.add(e.location)
                total += 1

        if total > 0:
            cumulative.divide(total)
            cumulative.subtract(self.location)
            cumulative.set_magnitude(self.default_move_speed)

            steer = Vector2(
                cumulative.x - self.velocity.x,
                cumulative.y - self.velocity.y
            )
            steer.limit(self.max_force)

        return steer

    def __update_flocking_behavior(self, scene_data):
        self.query_result = scene_data.entity_bin.query(
            Rect(
                self.x - self.view_radius,
                self.y - self.view_radius,
                self.view_radius * 2,
                self.view_radius * 2
            )
        )

        seperation = self.__separation()
        alignment = self.__alignment()
        cohesion = self.__cohesion()

        seperation.multiply(3)
        alignment.multiply(1)
        cohesion.multiply(0.5)

        self.steer = Vector2(
            seperation.x + alignment.x + cohesion.x,
            seperation.y + alignment.y + cohesion.y
        )

    def update(self, delta_time, scene_data):
        self._calculate_scaled_speed(delta_time)
        self.__update_flocking_behavior(scene_data)
        self._apply_force(delta_time)
        self._collision(scene_data)

    def draw(self, surface):
        self.circle.draw(surface)
