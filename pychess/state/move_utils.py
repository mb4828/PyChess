"""Utility functions for move logic."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pychess import constants

if TYPE_CHECKING:
    from .game_state import GameState


def get_piece_color(piece_code: str) -> str:
    """Extract the color character from a piece code.

    :param piece_code: Piece code (e.g. 'pl') or bare color ('l' or 'd')
    :return: 'l' for light or 'd' for dark
    """
    if 'l' in piece_code:
        return 'l'
    return 'd'


def is_same_color(piece_code_a: str, piece_code_b: str) -> bool:
    """Check whether two pieces belong to the same player.

    :param piece_code_a: First piece code (e.g. 'pl')
    :param piece_code_b: Second piece code (e.g. 'pd')
    :return: True if both pieces share the same color
    """
    return get_piece_color(piece_code_a) == get_piece_color(piece_code_b)


def is_piece_at(game_state: GameState, x: int, y: int) -> bool:
    """Check if a piece exists at position (x, y) on the board.

    :param game_state: GameState representing the board
    :param x: Row index
    :param y: Column index
    :return: True if a piece occupies the square
    """
    code = game_state.get_piece(x, y)
    # '+' prefix is reserved for non-piece markers (e.g. en passant targets)
    return bool(code) and not code.startswith('+')


def in_bounds_x(x: int) -> bool:
    """Check if a row index is within the board.

    :param x: Row index
    :return: True if within bounds
    """
    return 0 <= x < constants.BOARD_WIDTH


def in_bounds_y(y: int) -> bool:
    """Check if a column index is within the board.

    :param y: Column index
    :return: True if within bounds
    """
    return 0 <= y < constants.BOARD_HEIGHT


def in_bounds(x: int, y: int) -> bool:
    """Check if a (row, col) position is within the board.

    :param x: Row index
    :param y: Column index
    :return: True if both coordinates are within bounds
    """
    return in_bounds_x(x) and in_bounds_y(y)
