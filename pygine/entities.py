from enum import IntEnum
import math
from pygame import Rect
from pygine.base import PygineObject
from pygine.draw import draw_rectangle
from pygine.geometry import Rectangle, Circle
from pygine import globals
from pygine.input import InputType, pressed, pressing
from pygine.maths import Vector2
from pygine.resource import Animation, Sprite, SpriteType
from pygine.sounds import play_sound
from pygine.utilities import CameraType, Color, Timer
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
        self.collision_width = 4
        self.collision_rectangles = [
            Rect(self.x + 2, self.y - self.collision_width,
                 self.width - 4, self.collision_width),
            Rect(self.x + 2, self.y + self.height,
                 self.width - 4, self.collision_width),
            Rect(self.x - self.collision_width, self.y + self.collision_width * 2,
                 self.collision_width, self.height - self.collision_width * 2 * 2),
            Rect(self.x + self.width, self.y + self.collision_width * 2,
                 self.collision_width, self.height - self.collision_width * 2 * 2)
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
        self.walk_animation = Animation(6, 6, 100)
        self.direction = Direction.NONE
        self.area = None
        self.query_result = None

        self.default_jump_height = 16 * 4
        self.jump_duration = 1
        self.default_run_acceleration = 10
        self.default_ground_friction = 7
        self.default_air_friction = 1

        self.jump_initial_velocity = 0
        self.gravity = 0
        self.lateral_acceleration = 0
        self.ground_friction = 0
        self.air_friction = 0

        self.grounded = False
        self.jumping = False
        self.attempt_block_shift = False
        self.attacked = False
        self.restart = False

    def revive(self):
        self.grounded = False
        self.jumping = False
        self.attempt_block_shift = False
        self.attacked = False
        self.restart = False
        self.velocity = Vector2(0, 0)
        self.sprite.set_frame(0, 6)

    def _calculate_scaled_speed(self, delta_time):
        super(Player, self)._calculate_scaled_speed(delta_time)

        time = 1 / delta_time * self.jump_duration

        self.jump_initial_velocity = 4 * self.default_jump_height / time
        self.gravity = 8 * self.default_jump_height / time**2

        self.lateral_acceleration = self.default_run_acceleration * delta_time
        self.ground_friction = self.default_ground_friction * delta_time
        self.air_friction = self.default_air_friction * delta_time

    def set_location(self, x, y):
        super(Player, self).set_location(x, y)
        self.sprite.set_location(self.x - 10, self.y - 16)

    def _apply_force(self, delta_time):
        self.velocity.y += self.gravity

        self.set_location(self.x + self.velocity.x, self.y + self.velocity.y)

    def _update_input(self, delta_time):
        if self.attacked:
            return

        if pressing(InputType.LEFT) and not pressing(InputType.RIGHT):
            self.velocity.x -= self.lateral_acceleration
            if self.velocity.x < -self.move_speed:
                self.velocity.x = -self.move_speed

            if not self.jumping:
                self.sprite.set_frame(self.walk_animation.current_frame, 6)

            self.direction = Direction.LEFT

        elif pressing(InputType.RIGHT) and not pressing(InputType.LEFT):
            self.velocity.x += self.lateral_acceleration
            if self.velocity.x > self.move_speed:
                self.velocity.x = self.move_speed

            if not self.jumping:
                self.sprite.set_frame(self.walk_animation.current_frame, 6)

            self.direction = Direction.RIGHT

        elif (
            (not pressing(InputType.LEFT) and not pressing(InputType.RIGHT)) or
            (pressing(InputType.LEFT) and pressing(InputType.RIGHT))
        ):
            if self.grounded:
                self.velocity.lerp(
                    Vector2(0, self.velocity.y), self.ground_friction)
            else:
                self.velocity.lerp(
                    Vector2(0, self.velocity.y), self.air_friction)

            if self.velocity.x > -0.1 and self.velocity.x < 0.1:
                self.velocity.x = 0

            self.sprite.set_frame(0, 6)

        if not self.grounded:
            if self.velocity.y < 0:
                self.sprite.set_frame(6, 6)
            if self.velocity.y > 0:
                self.sprite.set_frame(7, 6)
        else:
            if self.velocity.x == 0:
                if pressing(InputType.UP):
                    self.sprite.set_frame(8, 6)
                if pressing(InputType.DOWN):
                    self.sprite.set_frame(9, 6)

        if self.direction == Direction.LEFT:
            self.sprite.flip_horizontally(True)
        elif self.direction == Direction.RIGHT:
            self.sprite.flip_horizontally(False)

        if pressed(InputType.A) and self.grounded and not self.jumping:
            self.__jump(delta_time)
            self.jumping = True

        if self.jumping and self.velocity.y < -self.jump_initial_velocity / 2 and not pressing(InputType.A):
            self.velocity.y = -self.jump_initial_velocity / 2
            self.jumping = False

        if pressed(InputType.X):
            self.attempt_block_shift = True

    def __rectanlge_collision_logic(self, entity):
        # Bottom
        if self.velocity.y < 0 and self.collision_rectangles[0].colliderect(entity.bounds):
            self.set_location(self.x, entity.bounds.bottom)
            self.velocity.y = 0
        # Top
        if self.velocity.y > 0 and self.collision_rectangles[1].colliderect(entity.bounds):
            self.set_location(self.x, entity.bounds.top - self.bounds.height)
            self.grounded = True
            self.jumping = False
            self.velocity.y = 0

        # Right
        if self.velocity.x < 0 and self.collision_rectangles[2].colliderect(entity.bounds):
            self.set_location(entity.bounds.right, self.y)
            self.velocity.x = 0
        # Left
        if self.velocity.x > 0 and self.collision_rectangles[3].colliderect(entity.bounds):
            self.set_location(entity.bounds.left - self.bounds.width, self.y)
            self.velocity.x = 0

    def _collision(self, scene_data):
        if self.attacked:
            return

        if self.x < 3:
            self.set_location(3, self.y)

        if (globals.debugging):
            for e in scene_data.entities:
                e.set_color(Color.WHITE)

        self.area = Rect(
            self.x - 16,
            self.y - 32,
            self.width + 16 * 2,
            self.height + 32 * 2
        )

        self.grounded = False
        self.query_result = scene_data.entity_quad_tree.query(self.area)

        if self.attempt_block_shift:
            self.__shift_blocks(scene_data)

        self.attempt_block_shift = False

        for e in self.query_result:
            if e is self:
                continue

            if (globals.debugging):
                e.set_color(Color.RED)

            if isinstance(e, Block):
                self.__rectanlge_collision_logic(e)
                self._update_collision_rectangles()

            if isinstance(e, QBlock):
                if e.active:
                    self.__rectanlge_collision_logic(e)
                    self._update_collision_rectangles()

            if isinstance(e, BossCrab):
                if (
                    not e.hurt and
                    not self.grounded and
                    self.velocity.y > 0 and
                    self.collision_rectangles[1].colliderect(e.bounds)
                ):
                    e.bop_on_head()
                    self.velocity.y = -self.jump_initial_velocity * 0.35

        self.query_result = scene_data.kinetic_quad_tree.query(self.area)
        for e in self.query_result:
            if e is self:
                continue

            if (globals.debugging):
                e.set_color(Color.RED)

            if isinstance(e, Crab):
                if not e.dead:
                    if (
                        not e.aggravated and
                        not self.grounded and
                        self.velocity.y > 0 and
                        self.collision_rectangles[1].colliderect(e.bounds)
                    ):
                        e.squish()
                        self.velocity.y = -self.jump_initial_velocity * 0.35

                    elif e.aggravated and self.bounds.colliderect(e.bounds):
                        self.__finessed_by_enemy()

    def __jump(self, delta_time):
        self.velocity.y = -self.jump_initial_velocity
        play_sound("jump.wav")

    def __shift_blocks(self, scene_data):
        for e in self.query_result:
            if e is self:
                continue

            if isinstance(e, QBlock):
                if self.bounds.colliderect(e.bounds):
                    play_sound("shift_fail.wav")
                    return

        for e in scene_data.entities:
            if isinstance(e, QBlock):
                e.toggle()
            elif isinstance(e, Crab):
                e.toggle_aggravation()

        play_sound("shift.wav")

    def __finessed_by_enemy(self):
        self.attacked = True
        self.velocity.y = -self.jump_initial_velocity * 0.5
        self.sprite.set_frame(10, 6)

    def __update_death(self, scene_data):
        if self.y > scene_data.scene_bounds.height + 64:
            self.restart = True

    def __update_animation(self, delta_time):
        self.walk_animation.update(delta_time)

    def update(self, delta_time, scene_data):
        self._calculate_scaled_speed(delta_time)
        self._update_input(delta_time)
        self._apply_force(delta_time)
        self._update_collision_rectangles()
        self._collision(scene_data)
        self.__update_death(scene_data)
        self.__update_animation(delta_time)

    def draw(self, surface):
        if globals.debugging:
            self._draw_collision_rectangles(surface)
            draw_rectangle(
                surface,
                self.bounds,
                CameraType.DYNAMIC,
                self.color
            )
            if self.area != None:
                draw_rectangle(
                    surface,
                    self.area,
                    CameraType.DYNAMIC,
                    Color.BLACK,
                    1
                )
        else:
            self.sprite.draw(surface, CameraType.DYNAMIC)


class Crab(Kinetic):
    def __init__(self, x, y):
        super(Crab, self).__init__(x, y, 11, 9, 25)
        self.sprite = Sprite(self.x - 18, self.y - 19, SpriteType.CRAB)
        self.walk_animation = Animation(4, 4, 150)
        self.direction = Direction.RIGHT
        self.area = None
        self.query_result = None

        self.default_jump_height = 16 * 1.5
        self.jump_duration = 0.5

        self.jump_initial_velocity = 0
        self.gravity = 0
        self.lateral_acceleration = 0

        self.aggravated_move_speed = 100

        self.internal_bounds = Rect(self.x + 5, self.y + 5, 1, 1)

        self.grounded = False
        self.aggravated = False
        self.dead = False

    def set_location(self, x, y):
        super(Crab, self).set_location(x, y)
        self.sprite.set_location(self.x - 18, self.y - 19)
        self.internal_bounds = Rect(self.x + 5, self.y + 5, 1, 1)

    def toggle_aggravation(self):
        if self.dead:
            return

        self.aggravated = not self.aggravated

    def squish(self):
        self.dead = True
        self.velocity.y = -self.jump_initial_velocity * 0.75
        self.velocity.x = - \
            self.move_speed if randint(1, 10) % 2 == 0 else self.move_speed

    def _calculate_scaled_speed(self, delta_time):
        if self.aggravated:
            self.move_speed = self.aggravated_move_speed * delta_time
        else:
            self.move_speed = self.default_move_speed * delta_time

        time = 1 / delta_time * self.jump_duration

        self.jump_initial_velocity = 4 * self.default_jump_height / time
        self.gravity = 8 * self.default_jump_height / time**2

    def _apply_force(self, delta_time):
        self.velocity.y += self.gravity

        if self.direction == Direction.RIGHT:
            self.velocity.x = self.move_speed

        if self.direction == Direction.LEFT:
            self.velocity.x = -self.move_speed

        self.set_location(self.x + self.velocity.x, self.y + self.velocity.y)

    def _update_collision_rectangles(self):
        self.collision_width = 3
        self.collision_rectangles = [
            Rect(self.x + 2, self.y - self.collision_width * 2,
                 self.width - 4, self.collision_width * 2),
            Rect(self.x + 2, self.y + self.height,
                 self.width - 4, self.collision_width * 2),
            Rect(self.x - self.collision_width, self.y + self.collision_width,
                 self.collision_width, self.height - self.collision_width * 2),
            Rect(self.x + self.width, self.y + self.collision_width,
                 self.collision_width, self.height - self.collision_width * 2)
        ]

    def __rectanlge_collision_logic(self, entity):
        # Bottom
        if self.velocity.y < 0 and self.collision_rectangles[0].colliderect(entity.bounds):
            self.set_location(self.x, entity.bounds.bottom)
            self.velocity.y = 0

        # Top
        if self.velocity.y > 0 and self.collision_rectangles[1].colliderect(entity.bounds):
            self.set_location(self.x, entity.bounds.top - self.bounds.height)
            self.velocity.y = 0
            self.grounded = True

        # Right
        if self.velocity.x < 0 and self.collision_rectangles[2].colliderect(entity.bounds):
            self.set_location(entity.bounds.right, self.y)
            self.velocity.x = 0
            self.direction = Direction.RIGHT
        # Left
        if self.velocity.x > 0 and self.collision_rectangles[3].colliderect(entity.bounds):
            self.set_location(entity.bounds.left - self.bounds.width, self.y)
            self.velocity.x = 0
            self.direction = Direction.LEFT

    def _collision(self, scene_data):
        if self.dead:
            return

        if self.x < 3:
            self.set_location(3, self.y)
            self.velocity.x = 0
            self.direction = Direction.RIGHT

        if self.x + self.width > scene_data.scene_bounds.width:
            self.set_location(
                scene_data.scene_bounds.width - self.width, self.y)
            self.velocity.x = 0
            self.direction = Direction.LEFT

        if self.y > scene_data.scene_bounds.height + 64:
            self.squish()

        self.area = Rect(
            self.x - 16,
            self.y - 16,
            self.width + 16 * 2,
            self.height + 16 * 2
        )
        self.query_result = scene_data.entity_quad_tree.query(self.area)

        self.grounded = False

        for e in self.query_result:
            if e is self:
                continue

            if isinstance(e, Block):
                self.__rectanlge_collision_logic(e)
                self._update_collision_rectangles()

            elif isinstance(e, QBlock):
                if e.active:

                    if not self.dead and self.internal_bounds.colliderect(e.bounds):
                        self.squish()

                    self.__rectanlge_collision_logic(e)
                    self._update_collision_rectangles()

        self.query_result = scene_data.kinetic_quad_tree.query(self.area)
        for e in self.query_result:
            if e is self:
                continue

            if isinstance(e, Crab):
                self.__rectanlge_collision_logic(e)
                self._update_collision_rectangles()

    def __update_ai(self, scene_data):
        if self.dead:
            if self.y > scene_data.scene_bounds.height + 64:
                self.remove = True

        if self.aggravated:
            if self.grounded:
                self.velocity.y = -self.jump_initial_velocity

    def __update_animation(self, delta_time):
        self.walk_animation.update(delta_time)

        self.sprite.set_frame(
            self.walk_animation.current_frame, self.walk_animation.columns)

        if self.aggravated:
            self.sprite.increment_sprite_y(32)

        if self.dead:
            self.sprite.flip_vertically(True)

    def update(self, delta_time, scene_data):
        self._calculate_scaled_speed(delta_time)
        self.__update_ai(scene_data)
        self._apply_force(delta_time)
        self._update_collision_rectangles()
        self._collision(scene_data)
        self.__update_animation(delta_time)

    def draw(self, surface):
        if globals.debugging:
            self._draw_collision_rectangles(surface)
            draw_rectangle(
                surface,
                self.bounds,
                CameraType.DYNAMIC,
                self.color
            )
        else:
            self.sprite.draw(surface, CameraType.DYNAMIC)


class BossCrab(Entity):
    def __init__(self):
        super(BossCrab, self).__init__(96, 128, 128, 8)
        self.body = Sprite(self.x - 64, self.y - 32, SpriteType.CRAB_BOSS_BODY)    
        self.bandaid = Sprite(self.x + 2 * 16, self.y - 1 * 16, SpriteType.CRAB_BOSS_BANDAID)
        self.face = Sprite(self.x + 2 * 16, self.y + 2 * 16, SpriteType.CRAB_FACE_SLEEPING)
        self.emote = Sprite(self.x + 5 * 16, self.y - 2 * 16, SpriteType.CRAB_BOSS_EMOTE_SLEEPY)                            

        self.state_index = 0
        self.total_flashes = 3
        self.flashes = 0
        self.flash_duration = 200
        self.invinsibility_flash_timer = Timer(self.flash_duration)
        self.hurt = False
        self.flashing = False
        self.injured = False

    def bop_on_head(self):
        if not self.hurt:            
            self.state_index += 1
            self.hurt = True
            self.invinsibility_flash_timer.start()
                
            if self.state_index < 5:
                self.face.set_sprite(SpriteType.CRAB_FACE_HURT)
                self.emote.set_sprite(SpriteType.CRAB_BOSS_EMOTE_MAD)        

    def __update_ai(self, delta_time, scene_data):
        pass                   

    def __update_health(self, delta_time):
        if self.hurt:
            self.invinsibility_flash_timer.update(delta_time)

            if self.invinsibility_flash_timer.done:
                self.flashes += 1
                self.flashing = not self.flashing

                if self.flashes >= self.total_flashes * 2:                    
                    self.hurt = False
                    self.flashing = False
                    self.flashes = 0

                    if self.state_index == 1:
                        self.state_index += 1
                    if self.state_index < 5:
                        self.face.set_sprite(SpriteType.CRAB_FACE_HAPPY)
                        self.emote.set_sprite(SpriteType.NONE)

                self.invinsibility_flash_timer.reset()
                self.invinsibility_flash_timer.start()

    def __update_expression(self):
        if self.state_index >= 5:
            self.emote.set_sprite(SpriteType.CRAB_BOSS_EMOTE_THIRSTY)
            self.face.set_sprite(SpriteType.CRAB_FACE_INJURED)
            self.injured = True

    def update(self, delta_time, scene_data):
        self.__update_ai(delta_time, scene_data)
        self.__update_health(delta_time)
        self.__update_expression()

    def draw(self, surface):
        if globals.debugging:            
            draw_rectangle(surface, self.bounds,
                           CameraType.DYNAMIC, self.color, 4)
        else:
            if not self.flashing:
                self.body.draw(surface, CameraType.STATIC)
                self.bandaid.draw(surface, CameraType.STATIC)
                self.face.draw(surface, CameraType.STATIC)
                self.emote.draw(surface, CameraType.STATIC)              


class Claw(Kinetic):
    def __init__(self, boss, is_left):
        super(Claw, self).__init__(96, 128, 56, 74, 200)
        self.boss = boss
        self.is_left = is_left

        self.sprite = Sprite(self.x, self.y, SpriteType.CRAB_BOSS_ARM)

        if self.is_left:            
            self.set_location(self.x - 16, self.y + 6)
        else:            
            self.sprite.flip_horizontally(True)
            self.set_location(self.x + 5 * 16, self.y + 6)        

        self.initial_y = self.sprite.y
        self.windup = False
        self.slamming = False
        self.cooldown = False

    def set_location(self, x, y):
        super(Claw, self).set_location(x, y)
        if self.is_left:
            self.sprite.set_location(self.x, self.y)
        else:
            self.sprite.set_location(self.x, self.y)

    def _apply_force(self, delta_time):
        pass

    def _update_collision_rectangles(self):
        self.collision_width = 3
        self.collision_rectangles = [
            Rect(self.x + 2, self.y - self.collision_width * 2,
                 self.width - 4, self.collision_width * 2),
            Rect(self.x + 2, self.y + self.height,
                 self.width - 4, self.collision_width * 2),
            Rect(self.x - self.collision_width, self.y + self.collision_width,
                 self.collision_width, self.height - self.collision_width * 2),
            Rect(self.x + self.width, self.y + self.collision_width,
                 self.collision_width, self.height - self.collision_width * 2)
        ]

    def _collision(self, scene_data):
        pass

    def __update_ai(self, delta_time, scene_data):
        if self.boss.injured:
            return

        if (
            not self.boss.hurt and
            not self.slamming and
            not self.cooldown and
            scene_data.actor.y > self.initial_y and
            scene_data.actor.x >= self.x and 
            scene_data.actor.x <= self.x + self.width
            ):
            self.windup = True            

        if self.windup:
            if self.y > self.initial_y - 40:
                self.set_location(self.x, self.y - self.move_speed * 0.4) 
            else:
                self.slamming = True
                self.windup = False

        if self.slamming:
            if self.y + self.height < scene_data.scene_bounds.height - 8:
                self.set_location(self.x, self.y + self.move_speed * 3) 
            else:
                self.cooldown = True
                self.slamming = False

        if self.cooldown:
            if self.y > self.initial_y:
                self.set_location(self.x, self.y - self.move_speed * 0.07) 
            else:
                self.cooldown = False

    def update(self, delta_time, scene_data):
        self._calculate_scaled_speed(delta_time)
        self._apply_force(delta_time)
        self._update_collision_rectangles()
        self._collision(scene_data)
        self.__update_ai(delta_time, scene_data)

    def draw(self, surface):
        if globals.debugging:
            self._draw_collision_rectangles(surface)
            draw_rectangle(surface, self.bounds,
                           CameraType.DYNAMIC, self.color, 4)
        else:
            self.sprite.draw(surface, CameraType.STATIC)


class Block(Entity):
    def __init__(self, x, y, width, height):
        super(Block, self).__init__(x, y, width, height)
        #self.sprite = Sprite(self.x, self.y, SpriteType.SOLID_BLOCK)

    def update(self, delta_time, scene_data):
        pass

    def draw(self, surface):
        if globals.debugging:
            #self.sprite.draw(surface, CameraType.DYNAMIC)
            draw_rectangle(surface, self.bounds,
                           CameraType.DYNAMIC, self.color, 4)
        else:
            pass


class QBlock(Entity):
    def __init__(self, x, y, type):
        super(QBlock, self).__init__(x, y, 16, 16)
        self.active = False
        if type == 0:
            self.sprite = Sprite(self.x, self.y, SpriteType.Q_BLOCK_0)
        else:
            self.sprite = Sprite(self.x, self.y, SpriteType.Q_BLOCK_1)
            self.sprite.increment_sprite_y(16)
            self.active = True

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.sprite.increment_sprite_y(16)
        else:
            self.sprite.increment_sprite_y(-16)

    def update(self, delta_time, scene_data):
        pass

    def draw(self, surface):
        if globals.debugging:
            self.sprite.draw(surface, CameraType.DYNAMIC)
            draw_rectangle(surface, self.bounds,
                           CameraType.DYNAMIC, self.color, 2)
        else:
            self.sprite.draw(surface, CameraType.DYNAMIC)

