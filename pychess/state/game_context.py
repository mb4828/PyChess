"""Encapsulates game context: castling rights, en passant target, and turn tracking."""
from typing import Dict, Optional, Tuple

from .move_utils import get_piece_color


class GameContext:
    """Tracks game state beyond the board: castling rights, en passant, and turns."""

    def __init__(self) -> None:
        self.king_moved: Dict[str, bool] = {'l': False, 'd': False}
        self.rook_moved: Dict[str, Dict[int, bool]] = {
            'l': {0: False, 7: False},
            'd': {0: False, 7: False},
        }
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.is_light_turn: bool = True

    # ==== Castling Rights ==== #

    def has_king_moved(self, color: str) -> bool:
        """Check if the king of the given color has moved.

        :param color: 'l' or 'd'
        :return: True if the king has moved
        """
        return self.king_moved[color]

    def mark_king_moved(self, color: str) -> None:
        """Mark the king of the given color as having moved.

        :param color: 'l' or 'd'
        """
        self.king_moved[color] = True

    def has_rook_moved(self, color: str, col: int) -> bool:
        """Check if the rook at the given column has moved.

        :param color: 'l' or 'd'
        :param col: Column index (0 or 7)
        :return: True if the rook has moved
        """
        return self.rook_moved[color][col]

    def mark_rook_moved(self, color: str, col: int) -> None:
        """Mark the rook at the given column as having moved.

        :param color: 'l' or 'd'
        :param col: Column index (0 or 7)
        """
        self.rook_moved[color][col] = True

    # ==== En Passant ==== #

    def get_en_passant_target(self) -> Optional[Tuple[int, int]]:
        """Get the en passant target square, or None."""
        return self.en_passant_target

    def set_en_passant_target(self, target: Optional[Tuple[int, int]]) -> None:
        """Set the en passant target square. Pass None to clear.

        :param target: (row, col) tuple or None
        """
        self.en_passant_target = target

    # ==== Turn Management ==== #

    def switch_turn(self) -> None:
        """Switch to the other player's turn."""
        self.is_light_turn = not self.is_light_turn

    def current_color(self) -> str:
        """Return the color of the player whose turn it is ('l' or 'd')."""
        return 'l' if self.is_light_turn else 'd'

    def is_turn(self, piece_code: str) -> bool:
        """Check if it's the turn of the player who owns this piece.

        :param piece_code: Piece code (e.g. 'pl')
        :return: True if the piece belongs to the current player
        """
        color = get_piece_color(piece_code)
        return (self.is_light_turn and color == 'l') or (not self.is_light_turn and color == 'd')

    # ==== Serialization ==== #

    def to_dict(self) -> dict:
        """Build the context dict that move_validator expects.

        :return: Dict with 'king_moved', 'rook_moved', and 'en_passant_target'
        """
        return {
            'king_moved': self.king_moved,
            'rook_moved': self.rook_moved,
            'en_passant_target': self.en_passant_target,
        }
