""" Main game manager for PyChess. Responsible for kicking off games in different modes """

import pygame
from pychess.game.pvp_game import PVPGame


def new_pvp_game(window: pygame.Surface) -> PVPGame:
    """Start a new player vs. player game."""
    return PVPGame(window)
