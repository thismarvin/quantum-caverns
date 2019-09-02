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

    def _update_input(self, delta_time):
        raise NotImplementedError(
            "A class that inherits Actor did not implement the _update_input(delta_time) method")


class Player(Actor):
    def __init__(self, x, y):
        super(Player, self).__init__(x, y, 12, 28, 100)
        self.sprite = Sprite(self.x - 10, self.y - 16, SpriteType.PLAYER)
        self.query_result = None

        self.gravity = 9
        self.jump_height = 300
        self.grounded = False
        self.jumping = False

    def set_location(self, x, y):
        super(Player, self).set_location(x, y)
        self.sprite.set_location(self.x - 10, self.y - 16)

    def _apply_force(self, delta_time):

        self.velocity.y += self.gravity * delta_time

        self.set_location(self.x + self.velocity.x, self.y + self.velocity.y)

    def _update_input(self, delta_time):
        #if pressing(InputType.UP) and not pressing(InputType.DOWN):
        #    self.velocity.y = -1 * self.move_speed
#
        #if pressing(InputType.DOWN) and not pressing(InputType.UP):
        #    self.velocity.y = 1 * self.move_speed
#
        #if not pressing(InputType.UP) and not pressing(InputType.DOWN):
        #    self.velocity.y = 0

        if pressing(InputType.LEFT) and not pressing(InputType.RIGHT):
            self.velocity.x = -1 * self.move_speed

        if pressing(InputType.RIGHT) and not pressing(InputType.LEFT):
            self.velocity.x = 1 * self.move_speed

        if not pressing(InputType.LEFT) and not pressing(InputType.RIGHT):
            self.velocity.x = 0

        if pressing(InputType.A) and self.grounded and not self.jumping:
            self.__jump(delta_time)
            self.jumping = True
        
        if self.jumping and self.velocity.y < -self.jump_height / 2 * delta_time and not pressing(InputType.A):
            self.velocity.y = -self.jump_height / 2 * delta_time
            self.jumping = False

    def __rectanlge_collision_logic(self, entity):
        # Bottom
        if self.collision_rectangles[0].colliderect(entity.bounds) and self.velocity.y < 0:
            self.set_location(self.x, entity.bounds.bottom)
            self.velocity.y = 0
        # Top
        if self.collision_rectangles[1].colliderect(entity.bounds) and self.velocity.y > 0:
            self.set_location(self.x, entity.bounds.top - self.bounds.height)

            self.grounded = True
            self.jumping = False
            self.velocity.y = 0

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
           self.x - 16,
           self.y - 16,
           self.width + 16 * 2,
           self.height + 16 * 2
        )

        self.grounded = False
        self.query_result = scene_data.entity_bin.query(self.area)
        for e in self.query_result:
            if e is self:
                continue

            if (globals.debugging):
                e.set_color(Color.RED)

            if isinstance(e, Block):
                self.__rectanlge_collision_logic(e)
                self._update_collision_rectangles()


    def __jump(self, delta_time):
        self.velocity.y = -self.jump_height * delta_time        

    def update(self, delta_time, scene_data):
        self._calculate_scaled_speed(delta_time)
        self._update_input(delta_time)
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
            self.sprite.draw(surface, CameraType.DYNAMIC)
        else:
            self.sprite.draw(surface, CameraType.DYNAMIC)


class Block(Entity):
    def __init__(self, x, y):
        super(Block, self).__init__(x, y, 16, 16)
        self.sprite = Sprite(self.x, self.y, SpriteType.SOLID_BLOCK)

    def update(self, delta_time, scene_data):
        pass

    def draw(self, surface):
        if globals.debugging:
            draw_rectangle(surface, self.bounds,
                           CameraType.DYNAMIC, self.color)
        else:
            self.sprite.draw(surface, CameraType.DYNAMIC)


