"""
Logic to handle piece movement.
"""


def execute_move(game_state, piece_code, start_x, start_y, end_x, end_y, is_en_passant=False):
    """
    Executes a move. Moves are assumed to be valid. Handles castling and en passant.
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param start_x: Starting x position
    :param start_y: Starting y position
    :param end_x: Ending x position
    :param end_y: Ending y position
    :param is_en_passant: Whether this move is an en passant capture
    :return: New game state object with the move complete
    """
    game_state[start_x][start_y] = ''
    game_state[end_x][end_y] = piece_code

    # castling: king moved 2 squares horizontally - also move the rook
    if piece_code.startswith('k') and abs(end_y - start_y) == 2:
        if end_y == 6:  # kingside
            game_state[end_x][5] = game_state[end_x][7]
            game_state[end_x][7] = ''
        elif end_y == 2:  # queenside
            game_state[end_x][3] = game_state[end_x][0]
            game_state[end_x][0] = ''

    # en passant: remove the captured pawn (on the same row we started, same column we ended)
    if is_en_passant:
        game_state[start_x][end_y] = ''

    return game_state
