"""
Game sprites
"""

from math import floor

import pygame

import pychess.constants as constants
from .gui_utils import get_resource_path


class Sprites:
    def __init__(self, game_window):
        self.game_window = game_window

        # load sprites
        self.light_king = pygame.image.load(
            get_resource_path(constants.PATH_KL)).convert_alpha()
        self.dark_king = pygame.image.load(
            get_resource_path(constants.PATH_KD)).convert_alpha()
        self.light_queen = pygame.image.load(
            get_resource_path(constants.PATH_QL)).convert_alpha()
        self.dark_queen = pygame.image.load(
            get_resource_path(constants.PATH_QD)).convert_alpha()
        self.light_bishop = pygame.image.load(
            get_resource_path(constants.PATH_BL)).convert_alpha()
        self.dark_bishop = pygame.image.load(
            get_resource_path(constants.PATH_BD)).convert_alpha()
        self.light_knight = pygame.image.load(
            get_resource_path(constants.PATH_NL)).convert_alpha()
        self.dark_knight = pygame.image.load(
            get_resource_path(constants.PATH_ND)).convert_alpha()
        self.light_rook = pygame.image.load(
            get_resource_path(constants.PATH_RL)).convert_alpha()
        self.dark_rook = pygame.image.load(
            get_resource_path(constants.PATH_RD)).convert_alpha()
        self.light_pawn = pygame.image.load(
            get_resource_path(constants.PATH_PL)).convert_alpha()
        self.dark_pawn = pygame.image.load(
            get_resource_path(constants.PATH_PD)).convert_alpha()

    def scale_sprite(self, sprite, width, height):
        """
        Scales a sprite to a given width and height. If non-integers are passed for width/height they will be floor'd
        :param sprite: Surface containing the sprite
        :param width: Sprite width
        :param height: Sprite height
        :return: Surface containing the scaled sprite
        """
        return pygame.transform.smoothscale(sprite, (floor(width), floor(height)))

    def get_sprite_from_code(self, piece_code, width=None, height=None):
        """
        Takes a piece code (e.g. 'bl') and returns the sprite (e.g. light_bishop).
        Optionally accepts width and height and will return a scaled sprite.
        :param piece_code: Code for the piece (e.g. 'bl')
        :param height: Width (optional)
        :param width: Height (optional)
        :return: Surface containing the sprite
        """
        if piece_code == 'kl':
            sprite = self.light_king
        elif piece_code == 'kd':
            sprite = self.dark_king
        elif piece_code == 'ql':
            sprite = self.light_queen
        elif piece_code == 'qd':
            sprite = self.dark_queen
        elif piece_code == 'bl':
            sprite = self.light_bishop
        elif piece_code == 'bd':
            sprite = self.dark_bishop
        elif piece_code == 'nl':
            sprite = self.light_knight
        elif piece_code == 'nd':
            sprite = self.dark_knight
        elif piece_code == 'rl':
            sprite = self.light_rook
        elif piece_code == 'rd':
            sprite = self.dark_rook
        elif piece_code == 'pl':
            sprite = self.light_pawn
        elif piece_code == 'pd':
            sprite = self.dark_pawn
        else:
            sprite = None

        if sprite:
            if width and height:
                return self.scale_sprite(sprite, width, height)
            return sprite
