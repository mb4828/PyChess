"""Move validation logic: legal moves, check, checkmate, and stalemate detection."""
from typing import List, Tuple

from pychess import constants
from .game_context import GameContext
from .game_state import GameState, Piece
from .move_utils import is_piece_at, in_bounds, get_piece_color, in_bounds_y, in_bounds_x, is_same_color


def get_valid_moves(
    game_state: GameState,
    game_context: GameContext,
    piece_code: str,
    start_x: int,
    start_y: int,
    ignore_check: bool = False,
) -> List[Tuple[int, int]]:
    """Return all legal destination squares for the given piece.

    :param game_state: GameState representing the board
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting row
    :param start_y: Starting column
    :param ignore_check: If True, skip check-legality filtering (used internally to avoid recursion)
    :param game_context: Optional GameContext with castling/en passant state
    :return: List of (row, col) tuples the piece can legally move to
    """
    if piece_code.startswith('k'):
        return get_valid_king_moves(game_state, piece_code, start_x, start_y, ignore_check, game_context)
    if piece_code.startswith('q'):
        return get_valid_queen_moves(game_state, piece_code, start_x, start_y, ignore_check)
    if piece_code.startswith('b'):
        return get_valid_bishop_moves(game_state, piece_code, start_x, start_y, ignore_check)
    if piece_code.startswith('n'):
        return get_valid_knight_moves(game_state, piece_code, start_x, start_y, ignore_check)
    if piece_code.startswith('r'):
        return get_valid_rook_moves(game_state, piece_code, start_x, start_y, ignore_check)
    return get_valid_pawn_moves(game_state, piece_code, start_x, start_y, ignore_check, game_context)


def is_in_check(game_state: GameState, piece_code_or_color: str) -> bool:
    """Determine whether the king of the given color is in check.

    :param game_state: GameState representing the board
    :param piece_code_or_color: A piece code (e.g. 'pl') or bare color ('l' or 'd')
    :return: True if the king is in check
    """
    color = get_piece_color(piece_code_or_color)
    opposing_color_moves: List[Tuple[int, int]] = []
    king_location = (0, 0)
    for x in range(constants.BOARD_WIDTH):
        for y in range(constants.BOARD_HEIGHT):
            piece = game_state.get_piece(x, y)
            if is_piece_at(game_state, x, y) and not is_same_color(piece, color):
                # Must ignore check here to avoid infinite mutual recursion
                valid_moves = get_valid_moves(game_state, GameContext(), piece, x, y, True)
                if valid_moves:
                    opposing_color_moves += valid_moves
            elif is_piece_at(game_state, x, y) and piece == Piece('k' + color):
                king_location = (x, y)
    return king_location in opposing_color_moves


def is_in_checkmate(game_state: GameState, piece_code_or_color: str) -> bool:
    """Determine whether the given color is in checkmate.

    :param game_state: GameState representing the board
    :param piece_code_or_color: A piece code or bare color
    :return: True if the player is in checkmate
    """
    color = get_piece_color(piece_code_or_color)

    if not is_in_check(game_state, color):
        return False

    return not _has_any_legal_move(game_state, color)


def is_in_stalemate(game_state: GameState, piece_code_or_color: str) -> bool:
    """Determine whether the given color is in stalemate (no legal moves, not in check).

    :param game_state: GameState representing the board
    :param piece_code_or_color: A piece code or bare color
    :return: True if the player is in stalemate
    """
    color = get_piece_color(piece_code_or_color)

    if is_in_check(game_state, color):
        return False

    return not _has_any_legal_move(game_state, color)


def _has_any_legal_move(game_state: GameState, color: str) -> bool:
    """Check if the given color has at least one legal move available.

    Temporarily removes each friendly piece to simulate drag_start behavior,
    then checks for valid moves.

    :param game_state: GameState representing the board
    :param color: 'l' or 'd'
    :return: True if any legal move exists
    """
    for x in range(constants.BOARD_WIDTH):
        for y in range(constants.BOARD_HEIGHT):
            piece = game_state.get_piece(x, y)
            if is_piece_at(game_state, x, y) and is_same_color(piece, color):
                game_state.clear_square(x, y)
                valid_moves = get_valid_moves(game_state, GameContext(), piece, x, y, False)
                game_state.set_piece(x, y, piece)
                if valid_moves:
                    return True
    return False


def can_occupy_square(
    game_state: GameState, piece_code: str, sqx: int, sqy: int, ignore_check: bool,
) -> bool:
    """Check whether a piece could legally occupy the target square.

    Does not validate movement rules — only checks for friendly-piece blocking
    and whether occupying the square would leave the king in check.

    :param game_state: GameState representing the board
    :param piece_code: Code for the piece attempting to move
    :param sqx: Target row
    :param sqy: Target column
    :param ignore_check: If True, skip check-legality filtering
    :return: True if the square can be occupied
    """
    if is_piece_at(game_state, sqx, sqy) and is_same_color(piece_code, game_state.get_piece(sqx, sqy)):
        return False
    if not ignore_check:
        temp_game_state = game_state.copy()
        temp_game_state.set_piece(sqx, sqy, piece_code)
        if is_in_check(temp_game_state, piece_code):
            return False
    return True


# ==== Per-Piece Move Generators ==== #

def get_valid_king_moves(
    game_state: GameState,
    piece_code: str,
    start_x: int,
    start_y: int,
    ignore_check: bool,
    game_context: GameContext,
) -> List[Tuple[int, int]]:
    """Return valid moves for the king, including castling.

    :param game_state: GameState representing the board
    :param piece_code: King piece code (e.g. 'kl')
    :param start_x: Starting row
    :param start_y: Starting column
    :param ignore_check: If True, skip check-legality filtering
    :param game_context: GameContext with castling state
    :return: List of valid (row, col) destinations
    """
    moves = []
    for x in range(start_x - 1, start_x + 2):
        for y in range(start_y - 1, start_y + 2):
            if in_bounds(x, y) and not (x == start_x and y == start_y):
                if can_occupy_square(game_state, piece_code, x, y, ignore_check):
                    moves.append((x, y))

    if not ignore_check:
        _add_castling_moves(game_state, piece_code, start_x, start_y, game_context, moves)

    return moves


def _add_castling_moves(
    game_state: GameState,
    piece_code: str,
    start_x: int,
    start_y: int,
    game_context: GameContext,
    moves: List[Tuple[int, int]],
) -> None:
    """Append castling destinations to moves if castling is legal.

    :param game_state: GameState representing the board
    :param piece_code: King piece code
    :param start_x: King's current row
    :param start_y: King's current column (expected to be 4)
    :param game_context: GameContext with castling state
    :param moves: List to append castling destinations to
    """
    color = get_piece_color(piece_code)
    row = 7 if color == 'l' else 0
    if start_x != row or start_y != 4:
        return
    if game_context.has_king_moved(color) or is_in_check(game_state, color):
        return

    # Kingside: rook at (row, 7), squares (row, 5) and (row, 6) must be empty
    if (not game_context.has_rook_moved(color, 7)
            and game_state.get_piece(row, 7) == Piece('r' + color)
            and not is_piece_at(game_state, row, 5)
            and not is_piece_at(game_state, row, 6)
            and _castle_path_safe(game_state, piece_code, row, 4, 6)):
        moves.append((row, 6))

    # Queenside: rook at (row, 0), squares (row, 1), (row, 2), (row, 3) must be empty
    if (not game_context.has_rook_moved(color, 0)
            and game_state.get_piece(row, 0) == Piece('r' + color)
            and not is_piece_at(game_state, row, 1)
            and not is_piece_at(game_state, row, 2)
            and not is_piece_at(game_state, row, 3)
            and _castle_path_safe(game_state, piece_code, row, 4, 2)):
        moves.append((row, 2))


def _castle_path_safe(
    game_state: GameState, king_code: str, row: int, start_col: int, end_col: int,
) -> bool:
    """Verify the king doesn't pass through or land on a checked square when castling.

    :param game_state: GameState representing the board
    :param king_code: King piece code
    :param row: The row the king is on
    :param start_col: King's starting column
    :param end_col: King's destination column
    :return: True if the path is safe
    """
    step = 1 if end_col > start_col else -1
    for col in range(start_col + step, end_col + step, step):
        temp_game_state = game_state.copy()
        temp_game_state.set_piece(row, col, king_code)
        if is_in_check(temp_game_state, king_code):
            return False
    return True


def get_valid_queen_moves(
    game_state: GameState, piece_code: str, start_x: int, start_y: int, ignore_check: bool,
) -> List[Tuple[int, int]]:
    """Return valid moves for the queen (horizontal + vertical + diagonal).

    :param game_state: GameState representing the board
    :param piece_code: Queen piece code
    :param start_x: Starting row
    :param start_y: Starting column
    :param ignore_check: If True, skip check-legality filtering
    :return: List of valid (row, col) destinations
    """
    return (
        _horizontal_moves(game_state, piece_code, start_x, start_y, ignore_check)
        + _vertical_moves(game_state, piece_code, start_x, start_y, ignore_check)
        + _diagonal_moves(game_state, piece_code, start_x, start_y, ignore_check)
    )


def get_valid_bishop_moves(
    game_state: GameState, piece_code: str, start_x: int, start_y: int, ignore_check: bool,
) -> List[Tuple[int, int]]:
    """Return valid moves for the bishop (diagonal only).

    :param game_state: GameState representing the board
    :param piece_code: Bishop piece code
    :param start_x: Starting row
    :param start_y: Starting column
    :param ignore_check: If True, skip check-legality filtering
    :return: List of valid (row, col) destinations
    """
    return _diagonal_moves(game_state, piece_code, start_x, start_y, ignore_check)


def get_valid_knight_moves(
    game_state: GameState, piece_code: str, start_x: int, start_y: int, ignore_check: bool,
) -> List[Tuple[int, int]]:
    """Return valid moves for the knight (L-shapes).

    :param game_state: GameState representing the board
    :param piece_code: Knight piece code
    :param start_x: Starting row
    :param start_y: Starting column
    :param ignore_check: If True, skip check-legality filtering
    :return: List of valid (row, col) destinations
    """
    candidates = [
        (start_x + 1, start_y - 2), (start_x + 1, start_y + 2),
        (start_x - 1, start_y - 2), (start_x - 1, start_y + 2),
        (start_x + 2, start_y - 1), (start_x + 2, start_y + 1),
        (start_x - 2, start_y - 1), (start_x - 2, start_y + 1),
    ]
    return [
        (x, y) for x, y in candidates
        if in_bounds(x, y) and can_occupy_square(game_state, piece_code, x, y, ignore_check)
    ]


def get_valid_rook_moves(
    game_state: GameState, piece_code: str, start_x: int, start_y: int, ignore_check: bool,
) -> List[Tuple[int, int]]:
    """Return valid moves for the rook (horizontal + vertical).

    :param game_state: GameState representing the board
    :param piece_code: Rook piece code
    :param start_x: Starting row
    :param start_y: Starting column
    :param ignore_check: If True, skip check-legality filtering
    :return: List of valid (row, col) destinations
    """
    return (
        _horizontal_moves(game_state, piece_code, start_x, start_y, ignore_check)
        + _vertical_moves(game_state, piece_code, start_x, start_y, ignore_check)
    )


def get_valid_pawn_moves(
    game_state: GameState,
    piece_code: str,
    start_x: int,
    start_y: int,
    ignore_check: bool,
    game_context: GameContext,
) -> List[Tuple[int, int]]:
    """Return valid moves for the pawn, including en passant.

    :param game_state: GameState representing the board
    :param piece_code: Pawn piece code (e.g. 'pl')
    :param start_x: Starting row
    :param start_y: Starting column
    :param ignore_check: If True, skip check-legality filtering
    :param game_context: GameContext with en passant state
    :return: List of valid (row, col) destinations
    """
    moves: List[Tuple[int, int]] = []
    if get_piece_color(piece_code) == 'l':
        _add_light_pawn_moves(game_state, start_x, start_y, game_context, moves)
    else:
        _add_dark_pawn_moves(game_state, start_x, start_y, game_context, moves)

    return [
        (x, y) for x, y in moves
        if can_occupy_square(game_state, piece_code, x, y, ignore_check)
    ]


def _add_light_pawn_moves(
    game_state: GameState, start_x: int, start_y: int, game_context: GameContext,
    moves: List[Tuple[int, int]],
) -> None:
    """Append candidate light-pawn moves (forward, capture, en passant) to moves list."""
    if not is_piece_at(game_state, start_x - 1, start_y):
        moves.append((start_x - 1, start_y))
    if (start_x == constants.BOARD_HEIGHT - 2
            and not is_piece_at(game_state, start_x - 1, start_y)
            and not is_piece_at(game_state, start_x - 2, start_y)):
        moves.append((start_x - 2, start_y))
    if in_bounds_y(start_y - 1) and is_piece_at(game_state, start_x - 1, start_y - 1):
        moves.append((start_x - 1, start_y - 1))
    if in_bounds_y(start_y + 1) and is_piece_at(game_state, start_x - 1, start_y + 1):
        moves.append((start_x - 1, start_y + 1))

    if game_context.get_en_passant_target() and start_x == 3:
        ep_x, ep_y = game_context.get_en_passant_target()
        if ep_x == start_x - 1 and abs(ep_y - start_y) == 1:
            moves.append((ep_x, ep_y))


def _add_dark_pawn_moves(
    game_state: GameState, start_x: int, start_y: int, game_context: GameContext,
    moves: List[Tuple[int, int]],
) -> None:
    """Append candidate dark-pawn moves (forward, capture, en passant) to moves list."""
    if not is_piece_at(game_state, start_x + 1, start_y):
        moves.append((start_x + 1, start_y))
    if (start_x == 1
            and not is_piece_at(game_state, start_x + 1, start_y)
            and not is_piece_at(game_state, start_x + 2, start_y)):
        moves.append((start_x + 2, start_y))
    if in_bounds_y(start_y - 1) and is_piece_at(game_state, start_x + 1, start_y - 1):
        moves.append((start_x + 1, start_y - 1))
    if in_bounds_y(start_y + 1) and is_piece_at(game_state, start_x + 1, start_y + 1):
        moves.append((start_x + 1, start_y + 1))

    if game_context.get_en_passant_target() and start_x == 4:
        ep_x, ep_y = game_context.get_en_passant_target()
        if ep_x == start_x + 1 and abs(ep_y - start_y) == 1:
            moves.append((ep_x, ep_y))


# ==== Sliding-Piece Helpers ==== #

def _horizontal_moves(
    game_state: GameState, piece_code: str, start_x: int, start_y: int, ignore_check: bool,
) -> List[Tuple[int, int]]:
    """Generate moves along the horizontal axis (rows)."""
    moves: List[Tuple[int, int]] = []
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


def _vertical_moves(
    game_state: GameState, piece_code: str, start_x: int, start_y: int, ignore_check: bool,
) -> List[Tuple[int, int]]:
    """Generate moves along the vertical axis (columns)."""
    moves: List[Tuple[int, int]] = []
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


def _diagonal_moves(
    game_state: GameState, piece_code: str, start_x: int, start_y: int, ignore_check: bool,
) -> List[Tuple[int, int]]:
    """Generate moves along the four diagonal axes."""
    moves: List[Tuple[int, int]] = []
    for dx, dy in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
        x, y = start_x + dx, start_y + dy
        while in_bounds(x, y):
            if can_occupy_square(game_state, piece_code, x, y, ignore_check):
                moves.append((x, y))
            if is_piece_at(game_state, x, y):
                break
            x, y = x + dx, y + dy
    return moves
