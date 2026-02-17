"""Encapsulates the chess board state (8x8 grid of pieces)."""
from copy import deepcopy
from typing import List, Optional

from .piece import Piece


class GameState:
    """Represents the 8x8 chess board."""

    def __init__(self, board: Optional[List[List[str]]] = None) -> None:
        self.board: List[List[str]] = board if board is not None else self._starting_board()

    def get_piece(self, x: int, y: int) -> str:
        """Get the piece code at position (x, y).

        :param x: Row index
        :param y: Column index
        :return: Piece code string, or '' if empty
        """
        return self.board[x][y]

    def set_piece(self, x: int, y: int, piece_code: str) -> None:
        """Place a piece at position (x, y).

        :param x: Row index
        :param y: Column index
        :param piece_code: Piece code to place (e.g. 'pl')
        """
        self.board[x][y] = piece_code

    def clear_square(self, x: int, y: int) -> None:
        """Clear the square at position (x, y).

        :param x: Row index
        :param y: Column index
        """
        self.board[x][y] = ''

    def is_piece_at(self, x: int, y: int) -> bool:
        """Check if a piece exists at position (x, y).

        :param x: Row index
        :param y: Column index
        :return: True if a piece occupies the square
        """
        code = self.board[x][y]
        return bool(code) and not code.startswith('+')

    def copy(self) -> 'GameState':
        """Create a deep copy of this game state.

        :return: New GameState with an independent copy of the board
        """
        return GameState(board=deepcopy(self.board))

    @staticmethod
    def empty() -> 'GameState':
        """Create a GameState with an empty board.

        :return: GameState with all squares empty
        """
        return GameState(board=[['' for _ in range(8)] for _ in range(8)])

    @staticmethod
    def _starting_board() -> List[List[str]]:
        """Create the standard chess starting position.

        :return: 8x8 list of piece code strings
        """
        return [
            [Piece.RD, Piece.ND, Piece.BD, Piece.QD, Piece.KD, Piece.BD, Piece.ND, Piece.RD],
            [Piece.PD, Piece.PD, Piece.PD, Piece.PD, Piece.PD, Piece.PD, Piece.PD, Piece.PD],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            [Piece.PL, Piece.PL, Piece.PL, Piece.PL, Piece.PL, Piece.PL, Piece.PL, Piece.PL],
            [Piece.RL, Piece.NL, Piece.BL, Piece.QL, Piece.KL, Piece.BL, Piece.NL, Piece.RL],
        ]
