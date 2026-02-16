"""Sprite loading and scaling for chess piece images."""
from math import floor
from typing import Dict, Optional

import pygame

from pychess import constants
from .gui_utils import get_resource_path


def _load_sprite(path: str) -> pygame.Surface:
    """Load and alpha-convert a sprite image.

    :param path: Relative path to the image asset
    :return: Alpha-converted pygame surface
    """
    return pygame.image.load(get_resource_path(path)).convert_alpha()


class Sprites:
    """Manages loading, caching, and scaling of chess piece sprites."""

    def __init__(self, game_window: pygame.Surface) -> None:
        self.game_window: pygame.Surface = game_window

        self._sprites: Dict[str, pygame.Surface] = {
            'kl': _load_sprite(constants.PATH_KL),
            'kd': _load_sprite(constants.PATH_KD),
            'ql': _load_sprite(constants.PATH_QL),
            'qd': _load_sprite(constants.PATH_QD),
            'bl': _load_sprite(constants.PATH_BL),
            'bd': _load_sprite(constants.PATH_BD),
            'nl': _load_sprite(constants.PATH_NL),
            'nd': _load_sprite(constants.PATH_ND),
            'rl': _load_sprite(constants.PATH_RL),
            'rd': _load_sprite(constants.PATH_RD),
            'pl': _load_sprite(constants.PATH_PL),
            'pd': _load_sprite(constants.PATH_PD),
        }

    def scale_sprite(self, sprite: pygame.Surface, width: float, height: float) -> pygame.Surface:
        """Scale a sprite to the given dimensions.

        Non-integer values are floored before scaling.

        :param sprite: Surface containing the sprite
        :param width: Target width in pixels
        :param height: Target height in pixels
        :return: Surface containing the scaled sprite
        """
        return pygame.transform.smoothscale(sprite, (floor(width), floor(height)))

    def get_sprite_from_code(
        self, piece_code: str, width: Optional[float] = None, height: Optional[float] = None,
    ) -> Optional[pygame.Surface]:
        """Look up a sprite by piece code, optionally scaling it.

        :param piece_code: Two-character piece code (e.g. 'bl' for light bishop)
        :param width: Target width in pixels, or None for original size
        :param height: Target height in pixels, or None for original size
        :return: The sprite surface, or None if the code is unrecognised
        """
        sprite = self._sprites.get(piece_code)

        if sprite and width and height:
            return self.scale_sprite(sprite, width, height)
        return sprite
