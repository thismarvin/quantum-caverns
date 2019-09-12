import os
import pygame
from pygame.mixer import Sound, music

MUSIC_PATH = ""
SOUND_PATH = ""
current_song = ""


def load_sound_paths():
    global MUSIC_PATH
    global SOUND_PATH

    path = os.path.dirname(os.path.abspath(__file__))

    MUSIC_PATH = path + '/assets/music/'
    SOUND_PATH = path + '/assets/sounds/'


def play_song(filename):
    global current_song
    global MUSIC_PATH
    if filename != current_song:
        music.load(MUSIC_PATH + filename)
        music.set_volume(0.75)
        music.play(-1)
        current_song = filename


def play_sound(filename):
    global SOUND_PATH

    sound = Sound(SOUND_PATH + filename)    
    sound.set_volume(0.75)
    sound.play()
