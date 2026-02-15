"""
Encapsulates the chess board state (8x8 grid of pieces).
"""
from copy import deepcopy

from .move_utils import is_piece_at as _is_piece_at


class GameState:
    """Represents the 8x8 chess board."""

    def __init__(self, board=None):
        self.board = board if board is not None else self._starting_board()

    def get_piece(self, x, y):
        """Get the piece code at position (x, y). Returns '' if empty."""
        return self.board[x][y]

    def set_piece(self, x, y, piece_code):
        """Place a piece at position (x, y)."""
        self.board[x][y] = piece_code

    def clear_square(self, x, y):
        """Clear the square at position (x, y)."""
        self.board[x][y] = ''

    def is_piece_at(self, x, y):
        """Check if a piece exists at position (x, y)."""
        return _is_piece_at(self.board, x, y)

    def copy(self):
        """Create a deep copy of this game state."""
        return GameState(board=deepcopy(self.board))

    @staticmethod
    def empty():
        """Factory method to create an empty board."""
        return GameState(board=[['' for _ in range(8)] for _ in range(8)])

    @staticmethod
    def _starting_board():
        """Create the standard chess starting position."""
        return [
            ['rd', 'nd', 'bd', 'qd', 'kd', 'bd', 'nd', 'rd'],
            ['pd', 'pd', 'pd', 'pd', 'pd', 'pd', 'pd', 'pd'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['pl', 'pl', 'pl', 'pl', 'pl', 'pl', 'pl', 'pl'],
            ['rl', 'nl', 'bl', 'ql', 'kl', 'bl', 'nl', 'rl']
        ]
