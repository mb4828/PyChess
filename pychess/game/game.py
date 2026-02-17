"""Base Game class containing shared game logic for all game modes."""
from math import floor
from typing import List, Optional, Tuple

import pygame
from pygame.event import Event

from pychess import constants
from pychess.gui.sounds import Sounds
from pychess.gui_manager import GUIManager
from pychess.state_manager import StateManager


class Game:
    """Base class for all game modes. Handles drag-and-drop piece movement, promotion, and post-move checks."""

    def __init__(self, window: pygame.Surface, sounds: Sounds) -> None:
        self.gui: GUIManager = GUIManager(window, sounds)
        self.state: StateManager = StateManager()

        self._dragging: bool = False
        self.drag_piece: str = ''
        self.drag_piece_start_sq: Tuple[int, int] = (0, 0)
        self.drag_piece_cursor_sq: Tuple[int, int] = (0, 0)
        self.drag_piece_cursor_pos: Tuple[int, int] = (0, 0)
        self.drag_piece_valid_moves: List[Tuple[int, int]] = []
        self.pending_promotion: Optional[Tuple[int, int]] = None

        self.gui.sounds.play_game_start()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame input event for this game mode.

        Subclasses can override to change or suppress input handling (e.g. blocking
        mouse events during an AI turn in PVC mode).

        :param event: The pygame event to process
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._dragging = True
            y, x = event.pos
            self.drag_start(x, y)
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            y, x = event.pos
            self.drag_continue(x, y)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
            self.drag_stop()

    def drag_start(self, x: int, y: int) -> None:
        """Begin dragging a piece from the square under the cursor.

        :param x: Mouse x coordinate (pixels)
        :param y: Mouse y coordinate (pixels)
        """
        self.drag_piece = ''
        sqx, sqy = floor(x / constants.SQ_HEIGHT), floor(y /
                                                         constants.SQ_HEIGHT)
        piece = self.state.get_piece(sqx, sqy)
        if piece and self.state.is_turn(piece):
            self.state.get_state().clear_square(sqx, sqy)
            self.drag_piece = piece
            self.drag_piece_start_sq = (sqx, sqy)
            self.drag_piece_cursor_sq = (sqx, sqy)
            self.drag_piece_valid_moves = self.state.get_valid_moves(self.drag_piece, sqx, sqy)

    def drag_continue(self, x: int, y: int) -> None:
        """Update the drag position as the cursor moves.

        :param x: Mouse x coordinate (pixels)
        :param y: Mouse y coordinate (pixels)
        """
        if self.drag_piece:
            sqx, sqy = floor(
                x / constants.SQ_HEIGHT), floor(y / constants.SQ_HEIGHT)
            self.drag_piece_cursor_sq = (sqx, sqy)
            self.drag_piece_cursor_pos = (x, y)

    def drag_stop(self) -> None:
        """Drop the held piece. Execute the move if valid, otherwise return it."""
        if not self.drag_piece:
            return

        if self.drag_piece_cursor_sq in self.drag_piece_valid_moves:
            self._execute_drag_move()
        elif self.drag_piece_cursor_sq != self.drag_piece_start_sq:
            self._return_piece_to_start()
            self.gui.sounds.play_error()
            self.drag_piece = ''
        else:
            # Piece dropped on starting square — keep highlights visible
            self._return_piece_to_start()
            return

        self.drag_piece = ''

    def _execute_drag_move(self) -> None:
        """Execute the dragged piece's move via the engine."""
        sqx, sqy = self.drag_piece_cursor_sq
        start_sqx, start_sqy = self.drag_piece_start_sq

        result = self.state.execute_move(
            self.drag_piece, start_sqx, start_sqy, sqx, sqy)

        if result['is_promotion']:
            self.pending_promotion = result['promotion_square']
            self.drag_piece = ''
            pygame.event.post(Event(constants.EVENT_PROMOTION))
            return

        self._on_move_complete(result['is_capture'])

    def _return_piece_to_start(self) -> None:
        """Place the dragged piece back on its starting square."""
        sqx, sqy = self.drag_piece_start_sq
        self.state.get_state().set_piece(sqx, sqy, self.drag_piece)

    def complete_promotion(self, piece_type: str) -> None:
        """Handle pawn promotion after the player selects a piece type.

        :param piece_type: The piece type character ('q', 'r', 'b', or 'n')
        """
        if self.pending_promotion:
            px, py = self.pending_promotion
            self.state.promote_pawn(px, py, piece_type)
            self.pending_promotion = None
            self._on_move_complete(False)

    def _on_move_complete(self, is_capture: bool) -> None:
        """Hook called after a valid move is executed.

        Subclasses can override to add mode-specific behavior (e.g. trigger AI move).

        :param is_capture: Whether the move captured an opponent's piece
        """
        self.state.switch_turn()
        self._post_move_checks(is_capture)

    def _post_move_checks(self, is_capture: bool) -> None:
        """Run check/checkmate/stalemate detection and play the appropriate sound.

        :param is_capture: Whether the move captured an opponent's piece
        """
        color = self.state.current_color()
        if self.state.is_in_checkmate(color):
            event_type = constants.EVENT_BLACK_WINS if color == 'l' else constants.EVENT_WHITE_WINS
            pygame.event.post(Event(event_type))
            self.gui.sounds.play_game_over()
        elif self.state.is_in_stalemate(color):
            pygame.event.post(Event(constants.EVENT_DRAW))
            self.gui.sounds.play_game_over()
        elif self.state.is_in_check(color):
            self.gui.sounds.play_piece_check()
        else:
            self.gui.sounds.play_piece_move(is_capture, 'd' in self.drag_piece)

    def draw(self) -> None:
        """Render the board, pieces, and overlays for the current frame."""
        self.gui.draw_board()
        self.gui.draw_pieces(self.state.get_state(), constants.BOARD_WIDTH, constants.BOARD_HEIGHT)
        self.gui.draw_overlays(
            self.drag_piece, self.drag_piece_start_sq,
            self.drag_piece_cursor_sq, self.drag_piece_cursor_pos,
            self.drag_piece_valid_moves,
        )
