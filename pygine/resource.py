import os
import pygame
from enum import IntEnum
from pygine.base import PygineObject
from pygine.draw import draw_image
from pygine import globals
from pygine.sounds import load_sound_paths
from pygine.utilities import Timer


SPRITE_SHEET = None
TEXT_SHEET = None


def load_content():
    global SPRITE_SHEET
    global TEXT_SHEET

    path = os.path.dirname(os.path.abspath(__file__))

    SPRITE_SHEET = pygame.image.load(
        path + "/assets/sprites/sprites.png"
    )
    TEXT_SHEET = pygame.image.load(
        path + "/assets/sprites/font.png"
    )
    load_sound_paths()


class SpriteType(IntEnum):
    NONE = 0
    TEXT = 1
    PLAYER = 2
    BLOCK = 3
    TILE = 4


class Sprite(PygineObject):
    def __init__(self, x, y, sprite_type=SpriteType.NONE):
        super(Sprite, self).__init__(x, y, 0, 0)
        self.set_sprite(sprite_type)

    def set_sprite(self, sprite_type):
        self.type = sprite_type
        self.__load_sprite()

    def set_frame(self, frame, columns):
        self.__sprite_x = self.__original_sprite_x + frame % columns * self.width
        self.__sprite_y = self.__original_sprite_y + \
            int(frame / columns) * self.height
        self.__apply_changes_to_sprite()

    def increment_sprite_x(self, increment):
        self.__sprite_x += increment
        self.__apply_changes_to_sprite()

    def increment_sprite_y(self, increment):
        self.__sprite_y += increment
        self.__apply_changes_to_sprite()

    def __sprite_setup(self, sprite_x=0, sprite_y=0, width=0, height=0):
        self.__original_sprite_x = sprite_x
        self.__original_sprite_y = sprite_y
        self.__sprite_x = sprite_x
        self.__sprite_y = sprite_y
        self.set_width(width)
        self.set_height(height)

    def __load_sprite(self):
        if self.type == SpriteType.NONE:
            self.__sprite_setup(1023, 1023, 1, 1)

        elif (self.type == SpriteType.TEXT):
            self.__sprite_setup(0, 0, 8, 8)

        elif (self.type == SpriteType.PLAYER):
            self.__sprite_setup(0, 0, 32, 32)
        elif (self.type == SpriteType.BLOCK):
            self.__sprite_setup(0, 32, 64, 32)
        elif (self.type == SpriteType.TILE):
            self.__sprite_setup(32, 0, 32, 32)

        self.__apply_changes_to_sprite()

    def __apply_changes_to_sprite(self):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.type == SpriteType.TEXT:
            self.image.blit(TEXT_SHEET, (0, 0),
                            (self.__sprite_x, self.__sprite_y, self.width, self.height))
        else:
            self.image.blit(SPRITE_SHEET, (0, 0),
                            (self.__sprite_x, self.__sprite_y, self.width, self.height))

    def draw(self, surface, camera_type):
        draw_image(surface, self.image, self.bounds, camera_type)


class Animation:
    def __init__(self, total_frames, columns, frame_duration):
        self.total_frames = total_frames
        self.columns = columns
        self.__frame_duration = frame_duration
        self.current_frame = 0
        self.__timer = Timer(self.__frame_duration)
        self.__timer.start()

    def update(self, delta_time):
        self.__timer.update(delta_time)
        if self.__timer.done:
            self.current_frame = self.current_frame + \
                1 if self.current_frame + 1 < self.total_frames else 0
            self.__timer.reset()
            self.__timer.start()


class Text(PygineObject):
    def __init__(self, x, y, value):
        super(Text, self).__init__(x, y, 8, 8)

        self.value = value
        self.set_value(self.value)

    def set_value(self, value):
        self.value = value

        self.sprites = []
        for i in range(len(self.value)):
            self.sprites.append(
                Sprite(self.x + i * self.width, self.y, SpriteType.TEXT))

        for i in range(len(self.value)):
            self.sprites[i].set_frame(ord(list(self.value)[i]), 16)

        self.sprites.sort(key=lambda e: -e.x)

    def draw(self, surface, camera_type):
        for s in self.sprites:
            s.draw(surface, camera_type)
