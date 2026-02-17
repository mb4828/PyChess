"""Logic to handle piece movement on the board."""
from typing import List


def execute_move(
    game_state: List[List[str]],
    piece_code: str,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    is_en_passant: bool = False,
) -> List[List[str]]:
    """Execute a move in-place. Moves are assumed to be valid.

    Handles castling rook repositioning and en passant pawn removal.

    :param game_state: 2-dimensional list representing the board
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting row
    :param start_y: Starting column
    :param end_x: Ending row
    :param end_y: Ending column
    :param is_en_passant: Whether this move is an en passant capture
    :return: The mutated game state
    """
    game_state[start_x][start_y] = ''
    game_state[end_x][end_y] = piece_code

    # Castling: king moved 2 squares horizontally, so also reposition the rook
    if piece_code.startswith('k') and abs(end_y - start_y) == 2:
        if end_y == 6:  # kingside
            game_state[end_x][5] = game_state[end_x][7]
            game_state[end_x][7] = ''
        elif end_y == 2:  # queenside
            game_state[end_x][3] = game_state[end_x][0]
            game_state[end_x][0] = ''

    # En passant: captured pawn sits on the starting row at the destination column
    if is_en_passant:
        game_state[start_x][end_y] = ''

    return game_state
