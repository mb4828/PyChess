"""Unified state manager for chess game logic.

Wraps game state, context, move validation, and move execution
into a single interface that any game mode can use.
"""
from typing import Dict, Tuple

from pgchess.state.game_state import GameState
from pgchess.state.game_context import GameContext
from pgchess.state import move_validator, move_executor, move_utils


class StateManager:
    """Game state manager that manages board state, game context, and move logic."""

    def __init__(self) -> None:
        self._state: GameState = GameState()
        self._context: GameContext = GameContext()

    # ==== Board Access ==== #

    def get_state(self) -> GameState:
        """Get the current game state (board configuration)."""
        return self._state

    def get_context(self) -> GameContext:
        """Get the current game context (turn, castling rights, en passant target)."""
        return self._context

    def get_piece(self, x: int, y: int) -> str:
        """Get the piece code at position (x, y).

        :param x: Row index
        :param y: Column index
        :return: Piece code string, or '' if empty
        """
        return self._state.get_piece(x, y)

    def is_piece_at(self, x: int, y: int) -> bool:
        """Check if a piece exists at position (x, y).

        :param x: Row index
        :param y: Column index
        :return: True if a piece occupies the square
        """
        return self._state.is_piece_at(x, y)

    # ==== Turn Management ==== #

    def current_color(self) -> str:
        """Return the color whose turn it is ('l' or 'd')."""
        return self._context.current_color()

    def switch_turn(self) -> None:
        """Switch to the other player's turn."""
        self._context.switch_turn()

    def is_turn(self, piece_code: str) -> bool:
        """Check if it's the turn of the player who owns this piece.

        :param piece_code: Piece code (e.g. 'pl')
        :return: True if the piece belongs to the current player
        """
        return self._context.is_turn(piece_code)

    # ==== Move Validation ==== #

    def get_valid_moves(self, piece_code: str, x: int, y: int) -> list[Tuple[int, int]]:
        """Get list of valid destination squares for a piece at (x, y).

        The piece should already be removed from the board (matching drag_start behavior).

        :param piece_code: Code for the piece (e.g. 'pl')
        :param x: Row the piece was picked up from
        :param y: Column the piece was picked up from
        :return: List of (row, col) tuples the piece can legally move to
        """
        return move_validator.get_valid_moves(self._state, self._context, piece_code, x, y)

    # ==== Move Execution ==== #

    def execute_move(self, piece_code: str, start_x: int, start_y: int, end_x: int, end_y: int) -> Dict[str, object]:
        """Execute a move and update all game state.

        Handles castling rook movement, en passant captures,
        castling rights updates, and en passant target updates.

        :param piece_code: Code for the piece being moved
        :param start_x: Starting row
        :param start_y: Starting column
        :param end_x: Destination row
        :param end_y: Destination column
        :return: Dict with 'is_capture', 'is_promotion', 'promotion_square'
        """
        # Pawn diagonal to empty square means en passant
        is_en_passant = (piece_code.startswith('p') and start_y != end_y
                         and not self._state.is_piece_at(end_x, end_y))

        is_capture = self._state.is_piece_at(end_x, end_y) or is_en_passant

        move_executor.execute_move(
            self._state, piece_code, start_x, start_y, end_x, end_y, is_en_passant)
        self._update_castling_rights(
            piece_code, start_x, start_y, end_x, end_y)
        self._update_en_passant(piece_code, start_x, start_y, end_x, end_y)

        is_promotion = False
        promotion_square = None
        if piece_code.startswith('p'):
            color = move_utils.get_piece_color(piece_code)
            promotion_row = 0 if color == 'l' else 7
            if end_x == promotion_row:
                is_promotion = True
                promotion_square = (end_x, end_y)

        return {
            'is_capture': is_capture,
            'is_promotion': is_promotion,
            'promotion_square': promotion_square,
        }

    def promote_pawn(self, x: int, y: int, piece_type: str) -> None:
        """Promote the pawn at (x, y) to the given piece type.

        :param x: Row of the pawn
        :param y: Column of the pawn
        :param piece_type: Target piece type ('q', 'r', 'b', or 'n')
        """
        color = move_utils.get_piece_color(self._state.get_piece(x, y))
        self._state.set_piece(x, y, piece_type + color)

    # ==== Game State Checks ==== #

    def is_in_check(self, color: str) -> bool:
        """Check if the given color's king is in check.

        :param color: 'l' for light or 'd' for dark
        :return: True if the king is in check
        """
        return move_validator.is_in_check(self._state, color)

    def is_in_checkmate(self, color: str) -> bool:
        """Check if the given color is in checkmate.

        :param color: 'l' for light or 'd' for dark
        :return: True if the player is in checkmate
        """
        return move_validator.is_in_checkmate(self._state, color)

    def is_in_stalemate(self, color: str) -> bool:
        """Check if the given color is in stalemate.

        :param color: 'l' for light or 'd' for dark
        :return: True if the player is in stalemate
        """
        return move_validator.is_in_stalemate(self._state, color)

    # ==== Private Helpers ==== #

    def _update_castling_rights(  # pylint: disable=unused-argument
        self, piece_code: str, start_x: int, start_y: int, end_x: int, end_y: int,
    ) -> None:
        """Update castling rights based on the move just made."""
        color = move_utils.get_piece_color(piece_code)

        if piece_code.startswith('k'):
            self._context.mark_king_moved(color)

        if piece_code.startswith('r'):
            if start_y == 0:
                self._context.mark_rook_moved(color, 0)
            elif start_y == 7:
                self._context.mark_rook_moved(color, 7)

        # A capture on a rook's home square also revokes that rook's castling rights
        if end_x in (0, 7) and end_y in (0, 7):
            target_color = 'l' if end_x == 7 else 'd'
            self._context.mark_rook_moved(target_color, end_y)

    def _update_en_passant(  # pylint: disable=unused-argument
        self, piece_code: str, start_x: int, start_y: int, end_x: int, end_y: int,
    ) -> None:
        """Update en passant target based on the move just made."""
        if piece_code.startswith('p') and abs(end_x - start_x) == 2:
            ep_x = (start_x + end_x) // 2
            self._context.set_en_passant_target((ep_x, end_y))
        else:
            self._context.set_en_passant_target(None)
