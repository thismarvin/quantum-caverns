import pygame
from pygine.maths import Vector2
from pygine.utilities import Camera, StaticCamera
from enum import IntEnum


class InputType(IntEnum):
    NONE = 0

    UP = 1
    LEFT = 2
    DOWN = 3
    RIGHT = 4
    A = 5
    B = 6
    X = 7
    Y = 8
    START = 9
    SELECT = 10

    RESET = 11
    TOGGLE_FULLSCREEN = 12
    TOGGLE_DEBUG = 13
    QUIT = 14


current_key_state = None
previous_key_state = None


def update_input():
    global current_key_state
    global previous_key_state

    previous_key_state = current_key_state
    current_key_state = pygame.key.get_pressed()

    if previous_key_state == None:
        previous_key_state = pygame.key.get_pressed()

def pressed(type):
    "Returns True if the key was just pressed and not held down the previous frame."
    if type == InputType.UP:
        return (not previous_key_state[pygame.K_UP] and current_key_state[pygame.K_UP]) or \
            (not previous_key_state[pygame.K_w]
             and current_key_state[pygame.K_w])
    if type == InputType.LEFT:
        return (not previous_key_state[pygame.K_LEFT] and current_key_state[pygame.K_LEFT]) or \
            (not previous_key_state[pygame.K_a]
             and current_key_state[pygame.K_a])
    if type == InputType.DOWN:
        return (not previous_key_state[pygame.K_DOWN] and current_key_state[pygame.K_DOWN]) or \
            (not previous_key_state[pygame.K_s]
             and current_key_state[pygame.K_s])
    if type == InputType.RIGHT:
        return (not previous_key_state[pygame.K_RIGHT] and current_key_state[pygame.K_RIGHT]) or \
            (not previous_key_state[pygame.K_d]
             and current_key_state[pygame.K_d])
    if type == InputType.A:
        return not previous_key_state[pygame.K_j] and current_key_state[pygame.K_j]
    if type == InputType.B:
        return not previous_key_state[pygame.K_k] and current_key_state[pygame.K_k]
    if type == InputType.X:
        return not previous_key_state[pygame.K_u] and current_key_state[pygame.K_u]
    if type == InputType.Y:
        return not previous_key_state[pygame.K_i] and current_key_state[pygame.K_i]
    if type == InputType.SELECT:
        return (not previous_key_state[pygame.K_SPACE] and current_key_state[pygame.K_SPACE]) or \
               (not previous_key_state[pygame.K_MINUS]
                and current_key_state[pygame.K_MINUS])
    if type == InputType.START:
        return (not previous_key_state[pygame.K_RETURN] and current_key_state[pygame.K_RETURN]) or \
               (not previous_key_state[pygame.K_PLUS]
                and current_key_state[pygame.K_PLUS])
    if type == InputType.RESET:
        return not previous_key_state[pygame.K_r] and current_key_state[pygame.K_r]
    if type == InputType.TOGGLE_FULLSCREEN:
        return not previous_key_state[pygame.K_F11] and current_key_state[pygame.K_F11]
    if type == InputType.TOGGLE_DEBUG:
        return (not previous_key_state[pygame.K_F3] and current_key_state[pygame.K_F3])
    if type == InputType.QUIT:
        return (not previous_key_state[pygame.K_ESCAPE] and current_key_state[pygame.K_ESCAPE]) or \
            (not previous_key_state[pygame.K_BACKSPACE]
             and current_key_state[pygame.K_BACKSPACE])

    return False


def pressing(type):
    "Returns True if the key is being pressed."
    if type == InputType.UP:
        return current_key_state[pygame.K_UP] or current_key_state[pygame.K_w]
    if type == InputType.LEFT:
        return current_key_state[pygame.K_LEFT] or current_key_state[pygame.K_a]
    if type == InputType.DOWN:
        return current_key_state[pygame.K_DOWN] or current_key_state[pygame.K_s]
    if type == InputType.RIGHT:
        return current_key_state[pygame.K_RIGHT] or current_key_state[pygame.K_d]
    if type == InputType.A:
        return current_key_state[pygame.K_j]
    if type == InputType.B:
        return current_key_state[pygame.K_k]
    if type == InputType.X:
        return current_key_state[pygame.K_u]
    if type == InputType.Y:
        return current_key_state[pygame.K_i]
    if type == InputType.SELECT:
        return current_key_state[pygame.K_SPACE] or current_key_state[pygame.K_MINUS]
    if type == InputType.START:
        return current_key_state[pygame.K_RETURN] or current_key_state[pygame.K_PLUS]
    if type == InputType.RESET:
        return current_key_state[pygame.K_r]
    if type == InputType.TOGGLE_FULLSCREEN:
        return current_key_state[pygame.K_F11]
    if type == InputType.TOGGLE_DEBUG:
        return current_key_state[pygame.K_F3] or \
            (pressing(InputType.START) and pressing(InputType.SELECT) and pressing(InputType.A))
    if type == InputType.QUIT:
        return current_key_state[pygame.K_ESCAPE] or current_key_state[pygame.K_BACKSPACE]

    return False


def get_dynamic_mouse_position():
    return Vector2(pygame.mouse.get_pos()[0] / Camera.scale + Camera.top_left.x / Camera.scale, pygame.mouse.get_pos()[1] / Camera.scale + Camera.top_left.y / Camera.scale)


def get_static_mouse_position():
    return Vector2(pygame.mouse.get_pos()[0] / Camera.scale, pygame.mouse.get_pos()[1] / Camera.scale)
