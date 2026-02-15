"""
Utility functions for move logic
"""

import pychess.constants as constants


def get_piece_color(piece_code):
    """
    Takes a piece code and returns its color
    :param piece_code: Piece code (e.g. 'pl')
    :return: Color ('l' or 'd')
    """
    if 'l' in piece_code:
        return 'l'
    return 'd'


def is_same_color(piece_code_a, piece_code_b):
    """
    Takes a piece code and returns a boolean indicating whether or not it's light
    :param piece_code_a: Piece code (e.g. 'pl')
    :param piece_code_b: Piece code (e.g. 'pd')
    :return: Boolean
    """
    return get_piece_color(piece_code_a) == get_piece_color(piece_code_b)


def is_piece_at(game_state, x, y):
    """
    Takes a game state, x, and y and indicates if there is a piece at that position
    :param game_state: 2 dimensional list representing game state
    :param x: x position of square to check
    :param y: y position of square to check
    :return: Boolean
    """
    # + is used for non-piece states like en passant opportunities so must be excluded
    # all other strings represent a piece
    return game_state[x][y] and not game_state[x][y].startswith('+')


def in_bounds_x(x):
    """
    Utility to determine if an x square position is within the board
    :param x: x square
    :return: Boolean
    """
    return 0 <= x < constants.BOARD_WIDTH


def in_bounds_y(y):
    """
    Utility to determine if a y square position is within the board
    :param y: y square
    :return: Boolean
    """
    return 0 <= y < constants.BOARD_HEIGHT


def in_bounds(x, y):
    """
    Utility to determine if an x, y square position is within the board
    :param x: x square
    :param y: y square
    :return: Boolean
    """
    return in_bounds_x(x) and in_bounds_y(y)
