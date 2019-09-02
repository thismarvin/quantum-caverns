import pygame
from enum import IntEnum
from pygine.maths import Vector2


class Color:
    "A convenient list of RGB colors."
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    SKY_BLUE = (41, 173, 255)
    GRASS_GREEN = (0, 168, 68)
    OCEAN_BLUE = (60, 188, 252)
    WOOD_BROWN = (172, 124, 0)
    GRAY = (120,120,120)
    LIGHT_GRAY = (188, 188, 188)
    LIGHT_BLUE = (104, 136, 252)
    LIGHT_PINK = (248, 164, 192)
    TEAL = (0, 136, 136)


class Timer:
    def __init__(self, length, started=False):
        self.length = length
        self.started = started
        self.done = False
        self.ticks = 0

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def reset(self):
        self.started = False
        self.done = False
        self.ticks = 0

    def update(self, delta_time):
        if self.started and not self.done:
            self.ticks += delta_time
            if self.ticks * 1000 >= self.length:
                self.done = True


class CameraType(IntEnum):
    DYNAMIC = 0
    STATIC = 1


class StaticCamera:
    BOUNDS = pygame.Rect(0, 0, 0, 0)
    scale = 0
    horizontal_letterbox = 0
    vertical_letterbox = 0
    top_left = Vector2()
    letterboxes = []

    def __init__(self, dimensions, scale):
        StaticCamera.horizontal_letterbox = 0
        StaticCamera.vertical_letterbox = 0
        StaticCamera.top_left = Vector2(
            -StaticCamera.horizontal_letterbox, - StaticCamera.vertical_letterbox)
        StaticCamera.scale = scale
        StaticCamera.BOUNDS = pygame.Rect(
            0, 0, dimensions[0], dimensions[1])

    def apply_horizontal_letterbox(self, horizontal_letterbox):
        StaticCamera.horizontal_letterbox = horizontal_letterbox
        StaticCamera.top_left.x = -StaticCamera.horizontal_letterbox

    def apply_vertical_letterbox(self, vertical_letterbox):
        StaticCamera.vertical_letterbox = vertical_letterbox
        StaticCamera.top_left.y = -StaticCamera.vertical_letterbox

    def draw(self, surface):
        # Top
        pygame.draw.rect(
            surface,
            Color.BLACK,
            (
                -32 * StaticCamera.scale,
                -32 * StaticCamera.scale,
                StaticCamera.BOUNDS.width * StaticCamera.scale + 64 * StaticCamera.scale,
                StaticCamera.vertical_letterbox + 32 * StaticCamera.scale
            )
        )

        # Bottom
        pygame.draw.rect(
            surface,
            Color.BLACK,
            (
                -32 * StaticCamera.scale,
                StaticCamera.vertical_letterbox +
                StaticCamera.BOUNDS.height * StaticCamera.scale,
                StaticCamera.BOUNDS.width * StaticCamera.scale + 64 * StaticCamera.scale,
                StaticCamera.vertical_letterbox + 32 * StaticCamera.scale
            )
        )

        # Left
        pygame.draw.rect(
            surface,
            Color.BLACK,
            (
                -32 * StaticCamera.scale,
                -32 * StaticCamera.scale,
                StaticCamera.horizontal_letterbox + 32 * StaticCamera.scale,
                StaticCamera.BOUNDS.height * StaticCamera.scale + 64 * StaticCamera.scale
            )
        )

        # Right
        pygame.draw.rect(
            surface,
            Color.BLACK,
            (
                StaticCamera.horizontal_letterbox +
                StaticCamera.BOUNDS.width * StaticCamera.scale,
                -32 * StaticCamera.scale,
                StaticCamera.horizontal_letterbox,
                StaticCamera.BOUNDS.height * StaticCamera.scale + 64 * StaticCamera.scale
            )
        )


class Camera:
    BOUNDS = pygame.Rect(0, 0, 0, 0)
    scale = 0
    top_left = Vector2()

    def __init__(self, top_left=Vector2(0, 0)):
        Camera.scale = StaticCamera.scale
        Camera.top_left.x = top_left.x - StaticCamera.horizontal_letterbox
        Camera.top_left.y = top_left.y - StaticCamera.vertical_letterbox
        Camera.BOUNDS = pygame.Rect(
            Camera.top_left.x, Camera.top_left.y, StaticCamera.BOUNDS.width, StaticCamera.BOUNDS.height)

    def stay_within_bounds(self, top_left, world_bounds):
        if world_bounds.width == 0 or world_bounds.height == 0:
            world_bounds = pygame.Rect(
                0, 0, Camera.BOUNDS.width, Camera.BOUNDS.height)

        if top_left.x < world_bounds.left:
            top_left.x = world_bounds.left
        if top_left.x + Camera.BOUNDS.width > world_bounds.right:
            top_left.x = world_bounds.right - Camera.BOUNDS.width
        if top_left.y < world_bounds.top:
            top_left.y = world_bounds.top
        if top_left.y + Camera.BOUNDS.height > world_bounds.bottom:
            top_left.y = world_bounds.bottom - Camera.BOUNDS.height

        Camera.top_left.x = top_left.x * Camera.scale - StaticCamera.horizontal_letterbox
        Camera.top_left.y = top_left.y * Camera.scale - StaticCamera.vertical_letterbox

    def get_viewport_top_left(self):
        return Vector2((Camera.top_left.x + StaticCamera.horizontal_letterbox) / Camera.scale, (Camera.top_left.y + StaticCamera.vertical_letterbox) / Camera.scale)

    def update(self, top_left=Vector2(0, 0), world_bounds=pygame.Rect(0, 0, 0, 0)):
        Camera.scale = StaticCamera.scale
        self.stay_within_bounds(top_left, world_bounds)
