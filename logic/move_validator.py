"""
Logic to check for valid/invalid moves
"""
from copy import deepcopy

import constants
from logic.move_utils import is_piece_at, in_bounds, get_piece_color, in_bounds_y, \
    in_bounds_x, is_same_color


def get_valid_moves(game_state, piece_code, start_x, start_y, ignore_check=False):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the piece
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :return: List of valid move pairs
    """
    if piece_code.startswith('k'):
        return get_valid_king_moves(game_state, piece_code, start_x, start_y, ignore_check)
    elif piece_code.startswith('q'):
        return get_valid_queen_moves(game_state, piece_code, start_x, start_y, ignore_check)
    elif piece_code.startswith('b'):
        return get_valid_bishop_moves(game_state, piece_code, start_x, start_y, ignore_check)
    elif piece_code.startswith('n'):
        return get_valid_knight_moves(game_state, piece_code, start_x, start_y, ignore_check)
    elif piece_code.startswith('r'):
        return get_valid_rook_moves(game_state, piece_code, start_x, start_y, ignore_check)
    else:
        return get_valid_pawn_moves(game_state, piece_code, start_x, start_y, ignore_check)


def is_in_check(game_state, piece_code_or_color):
    """
    Takes the state of the game and a color and returns a boolean indicating whether the king of that color is in check
    :param game_state: 2 dimensional list representing game state
    :param piece_code_or_color: A piece code or the color to validate check for (e.g 'pl' or 'l')
    :return: Boolean
    """
    # iterate over board, collecting opposing color moves and king location
    # the king is in check if opposing color moves includes its location since it's being attacked
    color = get_piece_color(piece_code_or_color)
    opposing_color_moves = []
    king_location = (0, 0)
    for x in range(0, constants.BOARD_WIDTH):
        for y in range(0, constants.BOARD_HEIGHT):
            piece = game_state[x][y]
            if is_piece_at(game_state, x, y) and not is_same_color(piece, color):
                # opposing piece found - collect valid moves
                valid_moves = get_valid_moves(game_state, piece, x, y, True)  # ignore check to avoid infinite loop!
                if len(valid_moves) > 0:
                    opposing_color_moves += valid_moves
            elif is_piece_at(game_state, x, y) and piece == 'k' + color:
                # king found - store location
                king_location = (x, y)
    return king_location in opposing_color_moves


def is_in_checkmate(game_state, piece_code_or_color):
    """
    Takes the state of the game and a color and returns a boolean indicating whether
    the king of that color is in checkmate.
    :param game_state: 2 dimensional list representing game state
    :param piece_code_or_color: A piece code or the color to validate check for (e.g 'pl' or 'l')
    :return: Boolean
    """
    # iterate over board, collecting active color moves
    # the king is in checkmate if there are no more valid moves
    color = get_piece_color(piece_code_or_color)
    active_color_moves = []
    for x in range(0, constants.BOARD_WIDTH):
        for y in range(0, constants.BOARD_HEIGHT):
            piece = game_state[x][y]
            if is_piece_at(game_state, x, y) and is_same_color(piece, color):
                # active piece found - collect valid moves
                if piece == 'kl':
                    pass
                valid_moves = get_valid_moves(game_state, piece, x, y, False)
                print(piece, valid_moves)
                if len(valid_moves) > 0:
                    active_color_moves += valid_moves
    if len(active_color_moves) == 0:
        return True
    return False


def can_occupy_square(game_state, piece_code, sqx, sqy, ignore_check):
    """
    Returns a boolean indicating whether a piece can occupy this square.
    Does not check if the piece can actually move here - use get_valid_moves() instead!
    :param game_state:
    :param piece_code:
    :param sqx:
    :param sqy:
    :param ignore_check:
    :return: Boolean
    """
    temp_game_state = deepcopy(game_state)
    temp_game_state[sqx][sqy] = piece_code
    if is_piece_at(game_state, sqx, sqy) and is_same_color(piece_code, game_state[sqx][sqy]):
        if piece_code == 'kl' and not ignore_check:
            print('OOPS 1', sqx, sqy)
        return False  # there's a piece on this square but we can't capture it
    if not ignore_check and is_in_check(temp_game_state, piece_code):
        if piece_code == 'kl' and not ignore_check:
            print('OOPS 2', sqx, sqy)
        return False  # this move would put us into check
    return True


def get_valid_king_moves(game_state, piece_code, start_x, start_y, ignore_check):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the King
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :return: List of valid move pairs
    """
    # The king can move one square in any direction and attack any opposite colored piece if it doesn't result in check
    # TODO the king can also castle left or right
    moves = []
    for x in range(start_x - 1, start_x + 2):
        for y in range(start_y - 1, start_y + 2):
            if in_bounds(x, y) and not (x == start_x and y == start_y):
                if can_occupy_square(game_state, piece_code, x, y, ignore_check):
                    moves.append((x, y))
    return moves


def get_valid_queen_moves(game_state, piece_code, start_x, start_y, ignore_check):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the Queen
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :return: List of valid move pairs
    """
    # The queen can move infinite squares vertically, horizontally, or diagonally
    # if a piece isn't blocking it or it doesn't result in check
    return horizontal_move_util(game_state, piece_code, start_x, start_y, ignore_check) + \
           vertical_move_util(game_state, piece_code, start_x, start_y, ignore_check) + \
           diagonal_move_util(game_state, piece_code, start_x, start_y, ignore_check)


def get_valid_bishop_moves(game_state, piece_code, start_x, start_y, ignore_check):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the Bishop
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :return: List of valid move pairs
    """
    # The bishop can move infinite squares diagonally if a piece isn't blocking it or it doesn't result in check
    return diagonal_move_util(game_state, piece_code, start_x, start_y, ignore_check)


def get_valid_knight_moves(game_state, piece_code, start_x, start_y, ignore_check):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the Knight
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :return: List of valid move pairs
    """
    # The knight can move in pairs of 1 vertical + 2 horizontal or 2 horizontal + 1 vertical
    # if a piece isn't blocking it or it doesn't result in check
    moves = [(start_x + 1, start_y - 2), (start_x + 1, start_y + 2), (start_x - 1, start_y - 2),
             (start_x - 1, start_y + 2), (start_x + 2, start_y - 1), (start_x + 2, start_y + 1),
             (start_x - 2, start_y - 1), (start_x - 2, start_y + 1)]
    i = 0
    while i < len(moves):
        move = moves[i]
        x, y = move
        if not in_bounds(x, y):
            moves.remove(move)  # filter out moves outside of the board
        elif not can_occupy_square(game_state, piece_code, x, y, ignore_check):
            moves.remove(move)  # filter out squares we can't occupy
        else:
            i += 1
    return moves


def get_valid_rook_moves(game_state, piece_code, start_x, start_y, ignore_check):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the Rook
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :return: List of valid move pairs
    """
    # The rook can move infinite squares horizontally or vertically
    # if a piece isn't blocking it or it doesn't result in check
    return horizontal_move_util(game_state, piece_code, start_x, start_y, ignore_check) + \
           vertical_move_util(game_state, piece_code, start_x, start_y, ignore_check)


def get_valid_pawn_moves(game_state, piece_code, start_x, start_y, ignore_check):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the Pawn
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :return: List of valid move pairs
    """
    # The pawn can move 2 squares vertically if on its first move otherwise 1 square vertically
    # if a piece isn't blocking it or it doesn't result in check.
    # It can also attack 1 square diagonally if a piece is present there or TODO diagonally en passant
    moves = []
    if get_piece_color(piece_code) == 'l':
        if not is_piece_at(game_state, start_x - 1, start_y):
            moves.append((start_x - 1, start_y))  # 1 forward for light
        if start_x == constants.BOARD_HEIGHT - 2 and not is_piece_at(game_state, start_x - 2, start_y):
            moves.append((start_x - 2, start_y))  # 2 forward for light
        if in_bounds_y(start_y - 1) and is_piece_at(game_state, start_x - 1, start_y - 1):
            moves.append((start_x - 1, start_y - 1))  # diagonal left light
        if in_bounds_y(start_y + 1) and is_piece_at(game_state, start_x - 1, start_y + 1):
            moves.append((start_x - 1, start_y + 1))  # diagonal right light
    else:
        if not is_piece_at(game_state, start_x + 1, start_y):
            moves.append((start_x + 1, start_y))  # 1 forward for dark
        if start_x == 1 and not is_piece_at(game_state, start_x + 2, start_y):
            moves.append((start_x + 2, start_y))  # 2 forward for dark
        if in_bounds_y(start_y - 1) and is_piece_at(game_state, start_x + 1, start_y - 1):
            moves.append((start_x + 1, start_y - 1))  # diagonal left dark
        if in_bounds_y(start_y + 1) and is_piece_at(game_state, start_x + 1, start_y + 1):
            moves.append((start_x + 1, start_y + 1))  # diagonal right dark

    # filter out squares we can't occupy
    i = 0
    while i < len(moves):
        move = moves[i]
        x, y = move
        if not can_occupy_square(game_state, piece_code, x, y, ignore_check):
            moves.remove(move)
        else:
            i += 1

    return moves


def horizontal_move_util(game_state, piece_code, start_x, start_y, ignore_check):
    moves = []
    x = start_x - 1
    while in_bounds_x(x):
        if can_occupy_square(game_state, piece_code, x, start_y, ignore_check):
            moves.append((x, start_y))
        if is_piece_at(game_state, x, start_y):
            break
        x -= 1
    x = start_x + 1
    while in_bounds_x(x):
        if can_occupy_square(game_state, piece_code, x, start_y, ignore_check):
            moves.append((x, start_y))
        if is_piece_at(game_state, x, start_y):
            break
        x += 1
    return moves


def vertical_move_util(game_state, piece_code, start_x, start_y, ignore_check):
    moves = []
    y = start_y - 1
    while in_bounds_y(y):
        if can_occupy_square(game_state, piece_code, start_x, y, ignore_check):
            moves.append((start_x, y))
        if is_piece_at(game_state, start_x, y):
            break
        y -= 1
    y = start_y + 1
    while in_bounds_y(y):
        if can_occupy_square(game_state, piece_code, start_x, y, ignore_check):
            moves.append((start_x, y))
        if is_piece_at(game_state, start_x, y):
            break
        y += 1
    return moves


def diagonal_move_util(game_state, piece_code, start_x, start_y, ignore_check):
    moves = []
    x, y = start_x + 1, start_y + 1
    while in_bounds(x, y):
        if can_occupy_square(game_state, piece_code, x, y, ignore_check):
            moves.append((x, y))
        if is_piece_at(game_state, x, y):
            break
        x, y = x + 1, y + 1
    x, y = start_x + 1, start_y - 1
    while in_bounds(x, y):
        if can_occupy_square(game_state, piece_code, x, y, ignore_check):
            moves.append((x, y))
        if is_piece_at(game_state, x, y):
            break
        x, y = x + 1, y - 1
    x, y = start_x - 1, start_y - 1
    while in_bounds(x, y):
        if can_occupy_square(game_state, piece_code, x, y, ignore_check):
            moves.append((x, y))
        if is_piece_at(game_state, x, y):
            break
        x, y = x - 1, y - 1
    x, y = start_x - 1, start_y + 1
    while in_bounds(x, y):
        if can_occupy_square(game_state, piece_code, x, y, ignore_check):
            moves.append((x, y))
        if is_piece_at(game_state, x, y):
            break
        x, y = x - 1, y + 1
    return moves
