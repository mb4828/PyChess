"""
Game sounds
"""

import pygame

import constants
from game.game_utils import get_resource_path


def play_game_start():
    sound = pygame.mixer.Sound(get_resource_path(constants.PATH_GAME_START))
    sound.play()


def play_game_over():
    sound = pygame.mixer.Sound(get_resource_path(constants.PATH_GAME_OVER))
    sound.play()


def play_error():
    sound = pygame.mixer.Sound(get_resource_path(constants.PATH_ERROR))
    sound.play()


def play_piece_move(is_dark=False):
    sound = pygame.mixer.Sound(get_resource_path(constants.PATH_PIECE_MOVE_2)) if is_dark \
        else pygame.mixer.Sound(get_resource_path(constants.PATH_PIECE_MOVE))
    sound.play()


def play_piece_capture():
    sound = pygame.mixer.Sound(get_resource_path(constants.PATH_PIECE_CAPTURE))
    sound.play()


def play_piece_check():
    sound = pygame.mixer.Sound(get_resource_path(constants.PATH_PIECE_CHECK))
    sound.play()
