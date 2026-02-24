"""Player-vs-Computer game mode. Human plays white; computer plays black."""
import logging
from threading import Thread
from typing import Optional, Tuple

import pygame
from pygame.event import Event

from pgchess import constants
from pgchess.engine.sunfish_adapter import SunfishAdapter
from pgchess.game.game import Game
from pgchess.gui.sounds import Sounds

logger = logging.getLogger(__name__)

# Color code for the computer's pieces
_COMPUTER_COLOR = 'd'


class PVCGame(Game):
    """Player-vs-Computer game mode. The human always plays white (light).

    After each human move the computer's response is computed in a background
    daemon thread.  When the search finishes, a :data:`~pgchess.constants.EVENT_COMPUTER_MOVE`
    pygame event is posted back to the main thread, which then calls
    :meth:`handle_event` to apply the move.

    Mouse events from the human are blocked while ``_computing`` is True to
    prevent out-of-turn moves.
    """

    def __init__(self, window: pygame.Surface, sounds: Sounds) -> None:
        super().__init__(window, sounds)
        self._engine: SunfishAdapter = SunfishAdapter()
        self._computing: bool = False
        self._last_computer_move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        """Dispatch a pygame event, applying a computer move or forwarding to the player.

        :param event: The pygame event to handle
        """
        if event.type == constants.EVENT_COMPUTER_MOVE:
            self._apply_computer_move(event.dict['move_data'])
            return
        # Block player input while the engine is thinking
        if not self._computing:
            super().handle_event(event)

    def _on_move_complete(self, is_capture: bool) -> None:
        """Hook called after any move completes. Triggers the computer's turn if applicable.

        :param is_capture: Whether the move captured an opponent's piece
        """
        super()._on_move_complete(is_capture)  # switches turn, runs post-move checks
        color = self.state.current_color()
        # Only start computing if it is now the computer's turn and the game is not already over
        if (
            color == _COMPUTER_COLOR
            and not self.state.is_in_checkmate(color)
            and not self.state.is_in_stalemate(color)
        ):
            self._last_computer_move = None
            self._start_compute()

    # ==== Computer move pipeline ==== #

    def _start_compute(self) -> None:
        """Kick off the engine search in a background thread."""
        self._computing = True
        Thread(target=self._compute_worker, daemon=True).start()

    def _compute_worker(self) -> None:
        """Run the engine search and post the result as a pygame event.

        Executes in the background thread; communicates back via pygame's
        event queue to remain thread-safe.
        """
        try:
            move_data = self._engine.get_best_move(
                self.state.get_state(), self.state.get_context()
            )
            pygame.event.post(Event(constants.EVENT_COMPUTER_MOVE, {'move_data': move_data}))
        except Exception:  # pylint: disable=broad-except
            logger.exception("Engine worker raised an unexpected exception")
            self._computing = False

    def _apply_computer_move(self, move_data: Tuple[int, int, int, int, str]) -> None:
        """Apply the computer's move to the board.

        The engine's output is trusted and is NOT re-validated by PGChess's
        own move validator.

        :param move_data: Tuple of ``(start_row, start_col, end_row, end_col, promotion)``
        """
        self._computing = False
        start_row, start_col, end_row, end_col, promo = move_data

        piece = self.state.get_piece(start_row, start_col)
        if not piece:
            logger.error(
                "Computer move references empty square (%d, %d) — ignoring",
                start_row, start_col,
            )
            return

        # Temporarily set drag_piece so _post_move_checks can play the correct sound
        self.drag_piece = piece
        self.state.get_state().clear_square(start_row, start_col)

        result = self.state.execute_move(piece, start_row, start_col, end_row, end_col)

        if result['is_promotion']:
            px, py = result['promotion_square']
            # Auto-promote to queen when no human preference is available
            self.state.promote_pawn(px, py, promo or 'q')

        self._last_computer_move = ((start_row, start_col), (end_row, end_col))
        self._on_move_complete(result['is_capture'])
        self.drag_piece = ''

    def _draw_board_highlights(self) -> None:
        """Highlight the computer's last move beneath the pieces."""
        if self._last_computer_move is not None:
            from_sq, to_sq = self._last_computer_move
            self.gui.draw_square_highlight(*from_sq)
            self.gui.draw_square_highlight(*to_sq)

    def draw(self) -> None:
        """Render the board and a 'Thinking...' indicator while the engine is searching."""
        super().draw()
        if self._computing:
            self._draw_thinking_label()

    def _draw_thinking_label(self) -> None:
        """Blit a small 'Thinking...' label in the top-left corner of the window."""
        font = pygame.font.SysFont(None, 24)
        label = font.render('Thinking...', True, (60, 60, 60))
        self.gui._window.blit(label, (6, 6))  # pylint: disable=protected-access
