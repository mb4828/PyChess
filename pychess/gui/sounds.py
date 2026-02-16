"""Sound effect playback functions."""
import pygame

from pychess import constants
from .gui_utils import get_resource_path


def _play(path: str) -> None:
    """Load and play a sound asset.

    :param path: Relative path to the sound file
    """
    pygame.mixer.Sound(get_resource_path(path)).play()


def play_game_start() -> None:
    """Play the game-start sound."""
    _play(constants.PATH_GAME_START)


def play_game_over() -> None:
    """Play the game-over sound."""
    _play(constants.PATH_GAME_OVER)


def play_error() -> None:
    """Play the invalid-move error sound."""
    _play(constants.PATH_ERROR)


def play_piece_move(is_dark: bool = False) -> None:
    """Play the piece-move sound.

    :param is_dark: If True, use the alternate sound for dark-player moves
    """
    path = constants.PATH_PIECE_MOVE_2 if is_dark else constants.PATH_PIECE_MOVE
    _play(path)


def play_piece_capture() -> None:
    """Play the piece-capture sound."""
    _play(constants.PATH_PIECE_CAPTURE)


def play_piece_check() -> None:
    """Play the check sound."""
    _play(constants.PATH_PIECE_CHECK)
