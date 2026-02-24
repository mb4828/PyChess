"""Tests for pgchess.game.pvc_game.PVCGame."""
from unittest.mock import MagicMock, patch

import pygame
import pytest
from pygame.event import Event

from pgchess import constants
from pgchess.game.pvc_game import PVCGame
from pgchess.gui.sounds import Sounds


def _sq_pos(row: int, col: int) -> tuple:
    """Return event.pos (px, py) for the center of board square (row, col).

    See test_game.py for the coordinate-swap explanation.
    event.pos = (col * SQ_HEIGHT + half, row * SQ_HEIGHT + half).
    """
    sq = constants.SQ_HEIGHT
    return (col * sq + sq // 2, row * sq + sq // 2)


@pytest.fixture
def pvc_game():
    """Create a PVCGame with a mocked GUIManager and a mocked SunfishAdapter."""
    window = MagicMock(spec=pygame.Surface)
    sounds = MagicMock(spec=Sounds)
    with patch('pgchess.game.game.GUIManager') as mock_gui_cls:
        mock_gui = MagicMock()
        mock_gui.sounds = MagicMock()
        mock_gui_cls.return_value = mock_gui
        with patch('pgchess.game.pvc_game.SunfishAdapter'):
            g = PVCGame(window, sounds)
    return g


class TestHandleEvent:
    def test_blocks_mouse_input_while_computing(self, pvc_game):
        """Mouse events should be ignored while the engine is computing."""
        pvc_game._computing = True
        pvc_game.handle_event(
            Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': _sq_pos(6, 4)})
        )
        # e2 pawn should not have been picked up
        assert pvc_game.drag_piece == ''

    def test_allows_mouse_input_when_not_computing(self, pvc_game):
        """Mouse events should be processed when the engine is idle."""
        pvc_game._computing = False
        pvc_game.handle_event(
            Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': _sq_pos(6, 4)})
        )
        # e2 white pawn (row=6, col=4) should be picked up
        assert pvc_game.drag_piece == 'pl'

    def test_computer_move_event_applies_pawn_advance(self, pvc_game):
        """EVENT_COMPUTER_MOVE should apply the engine's move to the board."""
        # Make it black's turn so _on_move_complete switches back to white (no re-compute)
        pvc_game.state.get_context().switch_turn()

        move_data = (1, 4, 3, 4, '')  # black pawn e7 → e5
        pvc_game.handle_event(
            Event(constants.EVENT_COMPUTER_MOVE, {'move_data': move_data})
        )

        assert pvc_game.state.get_piece(3, 4) == 'pd'
        assert pvc_game.state.get_piece(1, 4) == ''

    def test_computer_move_event_clears_computing_flag(self, pvc_game):
        """Handling EVENT_COMPUTER_MOVE should mark the engine as no longer computing."""
        pvc_game._computing = True
        pvc_game.state.get_context().switch_turn()  # black's turn

        move_data = (1, 4, 3, 4, '')
        pvc_game.handle_event(
            Event(constants.EVENT_COMPUTER_MOVE, {'move_data': move_data})
        )
        assert pvc_game._computing is False


class TestOnMoveComplete:
    def test_starts_compute_after_human_move(self, pvc_game):
        """After white's move, the engine should be triggered to compute black's reply."""
        with patch.object(pvc_game, '_start_compute') as mock_compute:
            with patch.object(pvc_game.state, 'is_in_checkmate', return_value=False):
                with patch.object(pvc_game.state, 'is_in_stalemate', return_value=False):
                    pvc_game._on_move_complete(is_capture=False)
        mock_compute.assert_called_once()

    def test_does_not_start_compute_on_checkmate(self, pvc_game):
        """Compute should not start if the game ended in checkmate."""
        with patch.object(pvc_game, '_start_compute') as mock_compute:
            with patch.object(pvc_game.state, 'is_in_checkmate', return_value=True):
                pvc_game._on_move_complete(is_capture=False)
        mock_compute.assert_not_called()

    def test_does_not_start_compute_on_stalemate(self, pvc_game):
        """Compute should not start if the game ended in stalemate."""
        with patch.object(pvc_game, '_start_compute') as mock_compute:
            with patch.object(pvc_game.state, 'is_in_checkmate', return_value=False):
                with patch.object(pvc_game.state, 'is_in_stalemate', return_value=True):
                    pvc_game._on_move_complete(is_capture=False)
        mock_compute.assert_not_called()


class TestApplyComputerMove:
    def test_places_piece_at_destination(self, pvc_game):
        """_apply_computer_move should relocate the piece from start to end square."""
        pvc_game.state.get_context().switch_turn()  # black's turn
        pvc_game._apply_computer_move((1, 4, 3, 4, ''))  # e7 → e5

        assert pvc_game.state.get_piece(3, 4) == 'pd'
        assert pvc_game.state.get_piece(1, 4) == ''

    def test_clears_computing_flag(self, pvc_game):
        """_apply_computer_move should set _computing to False before doing anything."""
        pvc_game._computing = True
        pvc_game.state.get_context().switch_turn()
        pvc_game._apply_computer_move((1, 4, 3, 4, ''))
        assert pvc_game._computing is False

    def test_ignores_move_from_empty_square(self, pvc_game):
        """A move referencing an empty source square should be silently skipped."""
        pvc_game._computing = True
        pvc_game._apply_computer_move((4, 4, 3, 4, ''))  # (4,4) is empty at start
        # _computing must be cleared regardless
        assert pvc_game._computing is False
        # No piece should appear at destination
        assert pvc_game.state.get_piece(3, 4) == ''

    def test_auto_promotes_to_specified_piece(self, pvc_game):
        """When the engine move reaches the promotion row, the pawn should be promoted.

        Black promotes at row 7 (rank 1). The pawn at a7 (1, 0) is moved to
        a1 (7, 0), capturing the white rook there; execute_move then triggers
        promotion and _apply_computer_move promotes to the engine's choice 'q'.
        """
        pvc_game.state.get_context().switch_turn()  # black's turn
        # Black pawn at a7 (1,0) → a1 (7,0): promotion row for black
        pvc_game._apply_computer_move((1, 0, 7, 0, 'q'))
        assert pvc_game.state.get_piece(7, 0) == 'qd'
