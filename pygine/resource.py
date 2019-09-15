import os
import pygame
from enum import IntEnum
from pygine.base import PygineObject
from pygine.draw import draw_image
from pygine import globals
from pygine.sounds import load_sound_paths
from pygine.utilities import Timer


SPRITE_SHEET = None
BOSS_SHEET = None
TEXT_SHEET = None

TOTAL_LEVELS_LOADED = 0
LAYER_LOOKUP = []
TOTAL_BOSSES_LOADED = 0
BOSS_LOOKUP = []

def load_content():
    global SPRITE_SHEET
    global BOSS_SHEET
    global TEXT_SHEET

    path = os.path.dirname(os.path.abspath(__file__))

    SPRITE_SHEET = pygame.image.load(
        path + "/assets/sprites/sprites.png"
    ).convert_alpha()
    BOSS_SHEET = pygame.image.load(
        path + "/assets/sprites/sprites_boss.png"
    ).convert_alpha()
    TEXT_SHEET = pygame.image.load(
        path + "/assets/sprites/font.png"
    ).convert_alpha()

    pygame_is_frustrating()
    load_sound_paths()


def pygame_is_frustrating():
    global TOTAL_LEVELS_LOADED
    global TOTAL_BOSSES_LOADED

    # Load normal levels
    path = os.path.dirname(os.path.abspath(__file__)) + "/assets/levels/"
    for f in os.listdir(path):
        TOTAL_LEVELS_LOADED += 1
    TOTAL_LEVELS_LOADED /= 2
    TOTAL_LEVELS_LOADED = int(TOTAL_LEVELS_LOADED)

    for i in range(TOTAL_LEVELS_LOADED):
        LAYER_LOOKUP.append(pygame.image.load(
            path + str(i) + ".png").convert_alpha())

    # Load boses
    path = os.path.dirname(os.path.abspath(__file__)) + "/assets/bosses/"
    for f in os.listdir(path):
        TOTAL_BOSSES_LOADED += 1
    TOTAL_BOSSES_LOADED /= 2
    TOTAL_BOSSES_LOADED = int(TOTAL_BOSSES_LOADED)

    for i in range(TOTAL_BOSSES_LOADED):
        BOSS_LOOKUP.append(pygame.image.load(
            path + str(i) + ".png").convert_alpha())            

    # Load Extra backgrounds
    path = os.path.dirname(os.path.abspath(__file__)) + \
        "/assets/sprites/layers/"
    for f in os.listdir(path):
        LAYER_LOOKUP.append(pygame.image.load(path + str(f)).convert())


class SpriteType(IntEnum):
    NONE = 0
    TEXT = 1

    SOLID_BLOCK = 3
    Q_BLOCK_0 = 4
    Q_BLOCK_1 = 5

    PLAYER = 6

    CRAB = 7
    
    CRAB_BOSS_BODY = 8
    CRAB_BOSS_ARM = 9
    CRAB_BOSS_BANDAID = 10
    CRAB_BOSS_EMOTE_MAD = 11
    CRAB_BOSS_EMOTE_THIRSTY = 12
    CRAB_BOSS_EMOTE_SLEEPY = 13
    CRAB_FACE = 14

    FALLING_ROCK_BIG = 15
    FALLING_ROCK_SMALL = 16

    TITLE = 17


class Sprite(PygineObject):
    def __init__(self, x, y, sprite_type=SpriteType.NONE):
        super(Sprite, self).__init__(x, y, 0, 0)
        self.part_of_boss = False
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

    def flip_horizontally(self, flip):
        if flip:
            self.image = pygame.transform.flip(
                self.image, True, False).convert_alpha()
        else:
            self.image = pygame.transform.flip(
                self.image, False, False).convert_alpha()

    def flip_vertically(self, flip):
        if flip:
            self.image = pygame.transform.flip(
                self.image, False, True).convert_alpha()
        else:
            self.image = pygame.transform.flip(
                self.image, False, False).convert_alpha()

    def __sprite_setup(self, sprite_x=0, sprite_y=0, width=0, height=0):
        self.__original_sprite_x = sprite_x
        self.__original_sprite_y = sprite_y
        self.__sprite_x = sprite_x
        self.__sprite_y = sprite_y
        self.set_width(width)
        self.set_height(height)

    def __load_sprite(self):
        if self.type == SpriteType.NONE:
            self.__sprite_setup(0, 0, 16, 16)

        elif (self.type == SpriteType.TEXT):
            self.__sprite_setup(0, 0, 8, 8)

        elif (self.type == SpriteType.SOLID_BLOCK):
            self.__sprite_setup(64, 32, 16, 16)
        elif (self.type == SpriteType.Q_BLOCK_0):
            self.__sprite_setup(0, 80, 16, 16)
        elif (self.type == SpriteType.Q_BLOCK_1):
            self.__sprite_setup(16, 80, 16, 16)

        elif (self.type == SpriteType.PLAYER):
            self.__sprite_setup(0, 160, 32, 48)

        elif (self.type == SpriteType.CRAB):
            self.__sprite_setup(32, 80, 48, 32)

            
        elif (self.type == SpriteType.FALLING_ROCK_BIG):
            self.__sprite_setup(0, 112, 32, 32)
        elif (self.type == SpriteType.FALLING_ROCK_BIG):
            self.__sprite_setup(0, 144, 16, 16)

        elif (self.type == SpriteType.CRAB_BOSS_BODY):
            self.part_of_boss = True
            self.__sprite_setup(0, 0, 256, 112)

        elif (self.type == SpriteType.CRAB_BOSS_ARM):
            self.part_of_boss = True
            self.__sprite_setup(0, 112, 64, 80)

        elif (self.type == SpriteType.CRAB_BOSS_BANDAID):
            self.part_of_boss = True
            self.__sprite_setup(64, 112, 64, 32)

        elif (self.type == SpriteType.CRAB_BOSS_EMOTE_MAD):
            self.part_of_boss = True
            self.__sprite_setup(128, 112, 32, 32)

        elif (self.type == SpriteType.CRAB_BOSS_EMOTE_THIRSTY):
            self.part_of_boss = True
            self.__sprite_setup(128, 144, 32, 32)

        elif (self.type == SpriteType.CRAB_BOSS_EMOTE_SLEEPY):
            self.part_of_boss = True
            self.__sprite_setup(160, 112, 80, 48)

        elif (self.type == SpriteType.CRAB_FACE):
            self.part_of_boss = True
            self.__sprite_setup(0, 192, 64, 32)

        elif (self.type == SpriteType.TITLE):
            self.__sprite_setup(0, 0, 64, 32)

        self.__apply_changes_to_sprite()

    def __apply_changes_to_sprite(self):
        self.image = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA).convert_alpha()

        if self.type == SpriteType.TEXT:
            self.image.blit(TEXT_SHEET, (0, 0),
                            (self.__sprite_x, self.__sprite_y, self.width, self.height))
        else:
            if not self.part_of_boss:
                self.image.blit(SPRITE_SHEET, (0, 0),
                                (self.__sprite_x, self.__sprite_y, self.width, self.height))
            else:
                self.image.blit(BOSS_SHEET, (0, 0),
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


class Layer(PygineObject):
    def __init__(self, index, is_level=True, is_boss=False):
        super(Layer, self).__init__(0, 0, 0, 0)
        self.index = index

        if is_level:
            self.set_width(40 * 16)
            self.set_height(15 * 16)
        else:
            self.set_width(20 * 16)
            self.set_height(15 * 16)
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if is_level and not is_boss:
            self.image = self.image.convert_alpha()            
            self.image.blit(
                LAYER_LOOKUP[int(self.index)], (0, 0), (0, 0, self.width, self.height))

        elif is_level and is_boss:
            self.image = self.image.convert_alpha()            
            self.image.blit(
                BOSS_LOOKUP[int(self.index)], (0, 0), (0, 0, self.width, self.height))
            
        else:
            self.image = self.image.convert()
            if str(os.path.dirname(os.path.abspath(__file__)))[:9] == "/home/cpi":
                panic = 0
                if self.index == 0:
                    panic = 1

                self.image.blit(
                    LAYER_LOOKUP[TOTAL_LEVELS_LOADED + panic],
                    (0, 0),
                    (0, 0, self.width, self.height)
                )          
            else:
                self.image.blit(
                    LAYER_LOOKUP[TOTAL_LEVELS_LOADED + self.index],
                    (0, 0),
                    (0, 0, self.width, self.height)
                )     

    def draw(self, surface, camera_type):
        draw_image(surface, self.image, self.bounds, camera_type)
