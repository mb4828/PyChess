"""
Encapsulates game context: castling rights, en passant target, and turn tracking.
"""
from .move_utils import get_piece_color


class GameContext:
    """Tracks game state beyond the board: castling rights, en passant, and turns."""

    def __init__(self):
        self.king_moved = {'l': False, 'd': False}
        self.rook_moved = {'l': {0: False, 7: False},
                           'd': {0: False, 7: False}}
        self.en_passant_target = None
        self.is_light_turn = True

    # --- Castling Rights ---

    def has_king_moved(self, color):
        """Check if the king of the given color has moved."""
        return self.king_moved[color]

    def mark_king_moved(self, color):
        """Mark the king of the given color as having moved."""
        self.king_moved[color] = True

    def has_rook_moved(self, color, col):
        """Check if the rook at the given column (0 or 7) has moved."""
        return self.rook_moved[color][col]

    def mark_rook_moved(self, color, col):
        """Mark the rook at the given column as having moved."""
        self.rook_moved[color][col] = True

    # --- En Passant ---

    def get_en_passant_target(self):
        """Get the en passant target square, or None."""
        return self.en_passant_target

    def set_en_passant_target(self, target):
        """Set the en passant target square. Pass None to clear."""
        self.en_passant_target = target

    # --- Turn Management ---

    def switch_turn(self):
        """Switch to the other player's turn."""
        self.is_light_turn = not self.is_light_turn

    def current_color(self):
        """Return the color of the player whose turn it is ('l' or 'd')."""
        return 'l' if self.is_light_turn else 'd'

    def is_turn(self, piece_code):
        """Check if it's the turn of the player who owns this piece."""
        color = get_piece_color(piece_code)
        return (self.is_light_turn and color == 'l') or (not self.is_light_turn and color == 'd')

    # --- Serialization ---

    def to_dict(self):
        """Build the context dict that move_validator expects."""
        return {
            'king_moved': self.king_moved,
            'rook_moved': self.rook_moved,
            'en_passant_target': self.en_passant_target,
        }
