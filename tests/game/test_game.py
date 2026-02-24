"""Tests for pgchess.game.game.Game."""
from unittest.mock import MagicMock, patch

import pygame
import pytest
from pygame.event import Event

from pgchess import constants
from pgchess.game.game import Game
from pgchess.gui.sounds import Sounds


def _sq_pos(row: int, col: int) -> tuple:
    """Return event.pos (px, py) for the center of board square (row, col).

    handle_event does ``y, x = event.pos``, so:
      - sqx (row) = floor(event.pos[1] / SQ_HEIGHT)
      - sqy (col) = floor(event.pos[0] / SQ_HEIGHT)

    Therefore: event.pos = (col * SQ_HEIGHT + half, row * SQ_HEIGHT + half).
    """
    sq = constants.SQ_HEIGHT
    return (col * sq + sq // 2, row * sq + sq // 2)


def _mousedown(pos):
    """Create a left-button MOUSEBUTTONDOWN event."""
    return Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': pos})


def _mousemove(pos):
    """Create a MOUSEMOTION event."""
    return Event(pygame.MOUSEMOTION, {'pos': pos})


def _mouseup(pos):
    """Create a left-button MOUSEBUTTONUP event."""
    return Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': pos})


@pytest.fixture
def game():
    """Create a Game with a mocked GUIManager and a real StateManager."""
    window = MagicMock(spec=pygame.Surface)
    sounds = MagicMock(spec=Sounds)
    with patch('pgchess.game.game.GUIManager') as mock_gui_cls:
        mock_gui = MagicMock()
        mock_gui.sounds = MagicMock()
        mock_gui_cls.return_value = mock_gui
        g = Game(window, sounds)
    return g


class TestDragStart:
    def test_picks_up_own_piece_on_click(self, game):
        """Clicking on a light piece during white's turn should begin dragging it."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))  # e2 — white pawn
        assert game.drag_piece == 'pl'
        assert game.drag_piece_start_sq == (6, 4)

    def test_does_not_pick_up_opponent_piece(self, game):
        """Clicking on a dark piece during white's turn should not start a drag."""
        game.handle_event(_mousedown(_sq_pos(1, 4)))  # e7 — black pawn
        assert game.drag_piece == ''

    def test_does_not_pick_up_empty_square(self, game):
        """Clicking on an empty square should not start a drag."""
        game.handle_event(_mousedown(_sq_pos(4, 4)))  # e4 — empty at game start
        assert game.drag_piece == ''

    def test_piece_removed_from_board_during_drag(self, game):
        """The picked-up piece should be cleared from the board while dragging."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))  # e2
        assert game.state.get_piece(6, 4) == ''

    def test_valid_moves_populated_on_pickup(self, game):
        """Legal destinations should be computed and stored when a piece is lifted."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))  # e2 — white pawn
        assert (4, 4) in game.drag_piece_valid_moves   # e4 (double advance)
        assert (5, 4) in game.drag_piece_valid_moves   # e3 (single advance)

    def test_knight_valid_moves_populated(self, game):
        """Knight at g1 should show its L-shaped moves."""
        game.handle_event(_mousedown(_sq_pos(7, 6)))  # g1 — white knight
        assert game.drag_piece == 'nl'
        assert len(game.drag_piece_valid_moves) > 0


class TestDragStop:
    def test_valid_drop_places_piece_at_destination(self, game):
        """Dropping on a legal square should move the piece there."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))  # pick up e2 pawn
        game.handle_event(_mousemove(_sq_pos(4, 4)))  # drag to e4
        game.handle_event(_mouseup(_sq_pos(4, 4)))
        assert game.state.get_piece(4, 4) == 'pl'
        assert game.state.get_piece(6, 4) == ''

    def test_invalid_drop_returns_piece_to_start(self, game):
        """Dropping on an illegal square should return the piece to its origin."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))  # e2 pawn
        game.handle_event(_mousemove(_sq_pos(3, 4)))  # e5 — not reachable in one move
        game.handle_event(_mouseup(_sq_pos(3, 4)))
        assert game.state.get_piece(6, 4) == 'pl'

    def test_invalid_drop_plays_error_sound(self, game):
        """Dropping on an illegal non-start square should play the error sound."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))  # e2 pawn
        game.handle_event(_mousemove(_sq_pos(3, 4)))  # e5
        game.handle_event(_mouseup(_sq_pos(3, 4)))
        game.gui.sounds.play_error.assert_called_once()

    def test_drop_on_start_square_returns_piece_silently(self, game):
        """Releasing a piece on its own square should restore it without an error sound."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))  # e2
        game.handle_event(_mouseup(_sq_pos(6, 4)))    # release on e2
        assert game.state.get_piece(6, 4) == 'pl'
        game.gui.sounds.play_error.assert_not_called()

    def test_turn_switches_after_valid_move(self, game):
        """Completing a valid move should hand the turn to the opponent."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))  # e2
        game.handle_event(_mousemove(_sq_pos(4, 4)))  # e4
        game.handle_event(_mouseup(_sq_pos(4, 4)))
        assert game.state.current_color() == 'd'

    def test_drag_piece_cleared_after_valid_drop(self, game):
        """drag_piece should be reset to '' once a valid move is completed."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))
        game.handle_event(_mousemove(_sq_pos(4, 4)))
        game.handle_event(_mouseup(_sq_pos(4, 4)))
        assert game.drag_piece == ''

    def test_drag_piece_cleared_after_invalid_drop(self, game):
        """drag_piece should be reset to '' after an invalid drop."""
        game.handle_event(_mousedown(_sq_pos(6, 4)))
        game.handle_event(_mousemove(_sq_pos(3, 4)))
        game.handle_event(_mouseup(_sq_pos(3, 4)))
        assert game.drag_piece == ''

    def test_no_drag_state_without_mousedown(self, game):
        """A MOUSEBUTTONUP with no preceding drag should have no effect."""
        game.handle_event(_mouseup(_sq_pos(4, 4)))
        assert game.drag_piece == ''
        assert game.state.current_color() == 'l'


class TestCompletePromotion:
    def test_promotes_pawn_to_queen(self, game):
        """complete_promotion should replace the pawn with the requested piece."""
        game.state.get_state().set_piece(0, 4, 'pl')
        game.pending_promotion = (0, 4)
        game.complete_promotion('q')
        assert game.state.get_piece(0, 4) == 'ql'

    def test_promotes_pawn_to_knight(self, game):
        """complete_promotion should support underpromotion to a knight."""
        game.state.get_state().set_piece(0, 4, 'pl')
        game.pending_promotion = (0, 4)
        game.complete_promotion('n')
        assert game.state.get_piece(0, 4) == 'nl'

    def test_clears_pending_promotion(self, game):
        """pending_promotion should be None after complete_promotion runs."""
        game.state.get_state().set_piece(0, 4, 'pl')
        game.pending_promotion = (0, 4)
        game.complete_promotion('q')
        assert game.pending_promotion is None

    def test_no_op_when_no_pending_promotion(self, game):
        """Calling complete_promotion without a pending promotion should do nothing."""
        game.pending_promotion = None
        game.complete_promotion('q')  # Should not raise
        assert game.pending_promotion is None


class TestPostMoveChecks:
    def test_checkmate_plays_game_over_sound(self, game):
        """When the current player is in checkmate, the game-over sound should play."""
        with patch.object(game.state, 'is_in_checkmate', return_value=True):
            game._post_move_checks(is_capture=False)
        game.gui.sounds.play_game_over.assert_called_once()

    def test_stalemate_plays_game_over_sound(self, game):
        """When the current player is in stalemate, the game-over sound should play."""
        with patch.object(game.state, 'is_in_checkmate', return_value=False):
            with patch.object(game.state, 'is_in_stalemate', return_value=True):
                game._post_move_checks(is_capture=False)
        game.gui.sounds.play_game_over.assert_called_once()

    def test_check_plays_check_sound(self, game):
        """When in check (not checkmate), the check sound should play."""
        with patch.object(game.state, 'is_in_checkmate', return_value=False):
            with patch.object(game.state, 'is_in_stalemate', return_value=False):
                with patch.object(game.state, 'is_in_check', return_value=True):
                    game._post_move_checks(is_capture=False)
        game.gui.sounds.play_piece_check.assert_called_once()

    def test_normal_move_plays_move_sound(self, game):
        """A non-capture, non-check move should play the piece-move sound."""
        with patch.object(game.state, 'is_in_checkmate', return_value=False):
            with patch.object(game.state, 'is_in_stalemate', return_value=False):
                with patch.object(game.state, 'is_in_check', return_value=False):
                    game._post_move_checks(is_capture=False)
        game.gui.sounds.play_piece_move.assert_called_once()

    def test_checkmate_does_not_play_move_sound(self, game):
        """On checkmate, the normal move sound must not play."""
        with patch.object(game.state, 'is_in_checkmate', return_value=True):
            game._post_move_checks(is_capture=False)
        game.gui.sounds.play_piece_move.assert_not_called()
