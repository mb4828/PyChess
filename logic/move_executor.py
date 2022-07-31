"""
Logic to handle piece movement.
"""


def execute_move(game_state, piece_code, end_x, end_y):
    """
    Executes a move. Moves are assumed to be valid. TODO Handles all sorts of corner cases like castles, en passants, etc.
    :param game_state: 2 dimensional list containing game state
    :param piece_code: Code for the piece (e.g. 'pl')
    :param end_x: Ending x position
    :param end_y: Ending y position
    :return: New game state object with the move complete
    """
    game_state[end_x][end_y] = piece_code
    return game_state
