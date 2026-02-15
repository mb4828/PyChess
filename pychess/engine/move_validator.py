"""
Logic to check for valid/invalid moves
"""
from copy import deepcopy

import pychess.constants as constants
from .move_utils import is_piece_at, in_bounds, get_piece_color, in_bounds_y, \
    in_bounds_x, is_same_color


def get_valid_moves(game_state, piece_code, start_x, start_y, ignore_check=False, game_context=None):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the piece
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :param game_context: Optional dict with castling/en passant state
    :return: List of valid move pairs
    """
    if piece_code.startswith('k'):
        return get_valid_king_moves(game_state, piece_code, start_x, start_y, ignore_check, game_context)
    elif piece_code.startswith('q'):
        return get_valid_queen_moves(game_state, piece_code, start_x, start_y, ignore_check)
    elif piece_code.startswith('b'):
        return get_valid_bishop_moves(game_state, piece_code, start_x, start_y, ignore_check)
    elif piece_code.startswith('n'):
        return get_valid_knight_moves(game_state, piece_code, start_x, start_y, ignore_check)
    elif piece_code.startswith('r'):
        return get_valid_rook_moves(game_state, piece_code, start_x, start_y, ignore_check)
    else:
        return get_valid_pawn_moves(game_state, piece_code, start_x, start_y, ignore_check, game_context)


def is_in_check(game_state, piece_code_or_color):
    """
    Takes the state of the game and a color and returns a boolean indicating whether the king of that color is in check
    :param game_state: 2 dimensional list representing game state
    :param piece_code_or_color: A piece code or the color to validate check for (e.g 'pl' or 'l')
    :return: Boolean
    """
    color = get_piece_color(piece_code_or_color)
    opposing_color_moves = []
    king_location = (0, 0)
    for x in range(0, constants.BOARD_WIDTH):
        for y in range(0, constants.BOARD_HEIGHT):
            piece = game_state[x][y]
            if is_piece_at(game_state, x, y) and not is_same_color(piece, color):
                # ignore check to avoid infinite loop!
                valid_moves = get_valid_moves(game_state, piece, x, y, True)
                if len(valid_moves) > 0:
                    opposing_color_moves += valid_moves
            elif is_piece_at(game_state, x, y) and piece == 'k' + color:
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
    color = get_piece_color(piece_code_or_color)

    # checkmate requires the king to be in check; no check = stalemate (not checkmate)
    if not is_in_check(game_state, color):
        return False

    # iterate over board, checking if any piece has a valid move that escapes check
    for x in range(0, constants.BOARD_WIDTH):
        for y in range(0, constants.BOARD_HEIGHT):
            piece = game_state[x][y]
            if is_piece_at(game_state, x, y) and is_same_color(piece, color):
                game_state[x][y] = ''
                valid_moves = get_valid_moves(game_state, piece, x, y, False)
                game_state[x][y] = piece  # restore piece
                if len(valid_moves) > 0:
                    return False
    return True


def is_in_stalemate(game_state, piece_code_or_color):
    """
    Takes the state of the game and a color and returns a boolean indicating whether
    that color is in stalemate (not in check but has no legal moves).
    :param game_state: 2 dimensional list representing game state
    :param piece_code_or_color: A piece code or the color to validate check for (e.g 'pl' or 'l')
    :return: Boolean
    """
    color = get_piece_color(piece_code_or_color)

    if is_in_check(game_state, color):
        return False

    for x in range(0, constants.BOARD_WIDTH):
        for y in range(0, constants.BOARD_HEIGHT):
            piece = game_state[x][y]
            if is_piece_at(game_state, x, y) and is_same_color(piece, color):
                game_state[x][y] = ''
                valid_moves = get_valid_moves(game_state, piece, x, y, False)
                game_state[x][y] = piece
                if len(valid_moves) > 0:
                    return False
    return True


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
    if is_piece_at(game_state, sqx, sqy) and is_same_color(piece_code, game_state[sqx][sqy]):
        return False  # there's a piece on this square but we can't capture it
    if not ignore_check:
        temp_game_state = deepcopy(game_state)
        temp_game_state[sqx][sqy] = piece_code
        if is_in_check(temp_game_state, piece_code):
            return False  # this move would put us into check
    return True


def get_valid_king_moves(game_state, piece_code, start_x, start_y, ignore_check, game_context=None):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the King
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'kl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :param game_context: Optional dict with castling state
    :return: List of valid move pairs
    """
    moves = []
    for x in range(start_x - 1, start_x + 2):
        for y in range(start_y - 1, start_y + 2):
            if in_bounds(x, y) and not (x == start_x and y == start_y):
                if can_occupy_square(game_state, piece_code, x, y, ignore_check):
                    moves.append((x, y))

    # castling
    if game_context and not ignore_check:
        color = get_piece_color(piece_code)
        row = 7 if color == 'l' else 0
        if start_x == row and start_y == 4:
            if not game_context['king_moved'][color] and not is_in_check(game_state, color):
                # kingside castle: rook at (row, 7), squares (row, 5) and (row, 6) must be empty
                if not game_context['rook_moved'][color][7]:
                    rook = game_state[row][7]
                    if rook == 'r' + color and \
                            not is_piece_at(game_state, row, 5) and \
                            not is_piece_at(game_state, row, 6):
                        if _castle_path_safe(game_state, piece_code, row, 4, 6):
                            moves.append((row, 6))

                # queenside castle: rook at (row, 0), squares (row, 1), (row, 2), (row, 3) must be empty
                if not game_context['rook_moved'][color][0]:
                    rook = game_state[row][0]
                    if rook == 'r' + color and \
                            not is_piece_at(game_state, row, 1) and \
                            not is_piece_at(game_state, row, 2) and \
                            not is_piece_at(game_state, row, 3):
                        if _castle_path_safe(game_state, piece_code, row, 4, 2):
                            moves.append((row, 2))

    return moves


def _castle_path_safe(game_state, king_code, row, start_col, end_col):
    """
    Checks that the king doesn't pass through or end on a square that's in check
    when castling from start_col to end_col.
    """
    step = 1 if end_col > start_col else -1
    for col in range(start_col + step, end_col + step, step):
        temp_game_state = deepcopy(game_state)
        temp_game_state[row][col] = king_code
        if is_in_check(temp_game_state, king_code):
            return False
    return True


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
    return horizontal_move_util(game_state, piece_code, start_x, start_y, ignore_check) + \
        vertical_move_util(game_state, piece_code, start_x, start_y, ignore_check) + \
        diagonal_move_util(game_state, piece_code,
                           start_x, start_y, ignore_check)


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
    moves = [(start_x + 1, start_y - 2), (start_x + 1, start_y + 2), (start_x - 1, start_y - 2),
             (start_x - 1, start_y + 2), (start_x + 2,
                                          start_y - 1), (start_x + 2, start_y + 1),
             (start_x - 2, start_y - 1), (start_x - 2, start_y + 1)]
    i = 0
    while i < len(moves):
        move = moves[i]
        x, y = move
        if not in_bounds(x, y):
            moves.remove(move)
        elif not can_occupy_square(game_state, piece_code, x, y, ignore_check):
            moves.remove(move)
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
    return horizontal_move_util(game_state, piece_code, start_x, start_y, ignore_check) + \
        vertical_move_util(game_state, piece_code,
                           start_x, start_y, ignore_check)


def get_valid_pawn_moves(game_state, piece_code, start_x, start_y, ignore_check, game_context=None):
    """
    Given the current game state and a starting x and y position, returns a list of valid move pairs for the Pawn
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param ignore_check: Boolean indicating whether check conditions should be ignored
    :param game_context: Optional dict with en passant state
    :return: List of valid move pairs
    """
    moves = []
    if get_piece_color(piece_code) == 'l':
        if not is_piece_at(game_state, start_x - 1, start_y):
            moves.append((start_x - 1, start_y))  # 1 forward for light
        if start_x == constants.BOARD_HEIGHT - 2 and not is_piece_at(game_state, start_x - 1, start_y) \
                and not is_piece_at(game_state, start_x - 2, start_y):
            moves.append((start_x - 2, start_y))  # 2 forward for light
        if in_bounds_y(start_y - 1) and is_piece_at(game_state, start_x - 1, start_y - 1):
            moves.append((start_x - 1, start_y - 1))  # diagonal left light
        if in_bounds_y(start_y + 1) and is_piece_at(game_state, start_x - 1, start_y + 1):
            moves.append((start_x - 1, start_y + 1))  # diagonal right light

        # en passant for light (light pawns on row 3 can capture en passant)
        if game_context and game_context['en_passant_target'] and start_x == 3:
            ep_x, ep_y = game_context['en_passant_target']
            if ep_x == start_x - 1 and abs(ep_y - start_y) == 1:
                moves.append((ep_x, ep_y))
    else:
        if not is_piece_at(game_state, start_x + 1, start_y):
            moves.append((start_x + 1, start_y))  # 1 forward for dark
        if start_x == 1 and not is_piece_at(game_state, start_x + 1, start_y) \
                and not is_piece_at(game_state, start_x + 2, start_y):
            moves.append((start_x + 2, start_y))  # 2 forward for dark
        if in_bounds_y(start_y - 1) and is_piece_at(game_state, start_x + 1, start_y - 1):
            moves.append((start_x + 1, start_y - 1))  # diagonal left dark
        if in_bounds_y(start_y + 1) and is_piece_at(game_state, start_x + 1, start_y + 1):
            moves.append((start_x + 1, start_y + 1))  # diagonal right dark

        # en passant for dark (dark pawns on row 4 can capture en passant)
        if game_context and game_context['en_passant_target'] and start_x == 4:
            ep_x, ep_y = game_context['en_passant_target']
            if ep_x == start_x + 1 and abs(ep_y - start_y) == 1:
                moves.append((ep_x, ep_y))

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
