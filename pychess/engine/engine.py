"""
Unified chess engine API. Wraps game state, context, move validation, and move execution
into a single interface that any game mode can use.
"""
from .game_state import GameState
from .game_context import GameContext
from . import move_validator, move_executor, move_utils


class GameEngine:
    """High-level chess engine that manages board state, game context, and move logic."""

    def __init__(self):
        self.state = GameState()
        self.context = GameContext()

    # --- Board Access ---

    def get_piece(self, x, y):
        """Get the piece code at position (x, y)."""
        return self.state.get_piece(x, y)

    def is_piece_at(self, x, y):
        """Check if a piece exists at position (x, y)."""
        return self.state.is_piece_at(x, y)

    # --- Turn Management ---

    def current_color(self):
        """Return the color whose turn it is ('l' or 'd')."""
        return self.context.current_color()

    def switch_turn(self):
        """Switch to the other player's turn."""
        self.context.switch_turn()

    def is_turn(self, piece_code):
        """Check if it's the turn of the player who owns this piece."""
        return self.context.is_turn(piece_code)

    # --- Move Validation ---

    def get_valid_moves(self, piece_code, x, y):
        """Get list of valid destination squares for a piece at (x, y).

        The piece should already be removed from the board (matching drag_start behavior).
        """
        return move_validator.get_valid_moves(
            self.state.board, piece_code, x, y,
            game_context=self.context.to_dict())

    # --- Move Execution ---

    def execute_move(self, piece_code, start_x, start_y, end_x, end_y):
        """Execute a move and update all game state.

        Handles castling rook movement, en passant captures,
        castling rights updates, and en passant target updates.

        :return: dict with 'is_capture', 'is_promotion', 'promotion_square'
        """
        # detect en passant before executing
        is_en_passant = (piece_code.startswith('p') and start_y != end_y and
                         not self.state.is_piece_at(end_x, end_y))

        is_capture = self.state.is_piece_at(end_x, end_y) or is_en_passant

        # execute the move (handles castling rook + en passant removal)
        move_executor.execute_move(
            self.state.board, piece_code, start_x, start_y, end_x, end_y, is_en_passant)

        # update castling rights
        self._update_castling_rights(
            piece_code, start_x, start_y, end_x, end_y)

        # update en passant target
        self._update_en_passant(piece_code, start_x, start_y, end_x, end_y)

        # detect promotion
        color = move_utils.get_piece_color(piece_code)
        is_promotion = False
        promotion_square = None
        if piece_code.startswith('p'):
            promotion_row = 0 if color == 'l' else 7
            if end_x == promotion_row:
                is_promotion = True
                promotion_square = (end_x, end_y)

        return {
            'is_capture': is_capture,
            'is_promotion': is_promotion,
            'promotion_square': promotion_square,
        }

    def promote_pawn(self, x, y, piece_type):
        """Promote the pawn at (x, y) to the given piece type ('q', 'r', 'b', 'n')."""
        color = move_utils.get_piece_color(self.state.get_piece(x, y))
        self.state.set_piece(x, y, piece_type + color)

    # --- Game State Checks ---

    def is_in_check(self, color):
        """Check if the given color's king is in check."""
        return move_validator.is_in_check(self.state.board, color)

    def is_in_checkmate(self, color):
        """Check if the given color is in checkmate."""
        return move_validator.is_in_checkmate(self.state.board, color)

    def is_in_stalemate(self, color):
        """Check if the given color is in stalemate."""
        return move_validator.is_in_stalemate(self.state.board, color)

    # --- Private Helpers ---

    def _update_castling_rights(self, piece_code, start_x, start_y, end_x, end_y):
        """Update castling rights based on the move just made."""
        color = move_utils.get_piece_color(piece_code)

        if piece_code.startswith('k'):
            self.context.mark_king_moved(color)

        if piece_code.startswith('r'):
            if start_y == 0:
                self.context.mark_rook_moved(color, 0)
            elif start_y == 7:
                self.context.mark_rook_moved(color, 7)

        # if a rook is captured, mark it as moved too
        if end_x in (0, 7) and end_y in (0, 7):
            target_color = 'l' if end_x == 7 else 'd'
            self.context.mark_rook_moved(target_color, end_y)

    def _update_en_passant(self, piece_code, start_x, start_y, end_x, end_y):
        """Update en passant target based on the move just made."""
        if piece_code.startswith('p') and abs(end_x - start_x) == 2:
            ep_x = (start_x + end_x) // 2
            self.context.set_en_passant_target((ep_x, end_y))
        else:
            self.context.set_en_passant_target(None)
