"""Tests for pgchess.gui.gui_manager: the GUI manager class."""
from math import floor
from unittest.mock import patch, MagicMock

import pygame

from pgchess import constants
from pgchess.gui.sounds import Sounds
from pgchess.state.game_state import GameState


def _make_gui():
    """Create a GUI instance with fully mocked pygame dependencies."""
    mock_surface = MagicMock()
    mock_surface.convert_alpha.return_value = mock_surface

    with patch('pgchess.gui.sprites.pygame.image.load', return_value=mock_surface):
        with patch('pgchess.gui.sprites.get_resource_path', side_effect=lambda p: p):
            with patch('pgchess.gui.sprites.pygame.transform.smoothscale', return_value=MagicMock()):
                from pgchess.gui_manager import GUIManager
                window = MagicMock(spec=pygame.Surface)
                gui = GUIManager(window, MagicMock(spec=Sounds))
                return gui, window


class TestDrawPiece:
    """Test piece drawing position calculations."""

    def test_blit_position_is_y_col_x_row(self):
        """draw_piece should blit at (SQ_HEIGHT * y, SQ_HEIGHT * x)."""
        gui, window = _make_gui()
        mock_sprite = MagicMock()
        sq = constants.SQ_HEIGHT

        with patch.object(gui._sprites, 'get_sprite_from_code', return_value=mock_sprite):
            gui.draw_piece('pl', 3, 5)
            window.blit.assert_called_once_with(mock_sprite, (sq * 5, sq * 3))

    def test_origin_position(self):
        """draw_piece at (0, 0) should blit at (0, 0)."""
        gui, window = _make_gui()
        mock_sprite = MagicMock()

        with patch.object(gui._sprites, 'get_sprite_from_code', return_value=mock_sprite):
            gui.draw_piece('kl', 0, 0)
            window.blit.assert_called_once_with(mock_sprite, (0, 0))

    def test_no_blit_when_sprite_missing(self):
        """draw_piece with an unknown code should not blit anything."""
        gui, window = _make_gui()

        with patch.object(gui._sprites, 'get_sprite_from_code', return_value=None):
            gui.draw_piece('xx', 0, 0)
            window.blit.assert_not_called()


class TestDrawDraggedPiece:
    """Test dragged piece rendering with scale-up behavior."""

    def test_scales_up_when_moved_away(self):
        """When cursor_sq differs from start_sq, piece should be scaled to 110%."""
        gui, window = _make_gui()
        mock_sprite = MagicMock()
        expected_scale = floor(constants.SQ_HEIGHT * 1.1)

        with patch.object(gui._sprites, 'get_sprite_from_code', return_value=mock_sprite) as mock_get:
            gui.draw_dragged_piece('pl', (200, 300), (3, 3), (4, 4))
            mock_get.assert_called_once_with(
                'pl', expected_scale, expected_scale)

    def test_scaled_piece_centered_on_cursor(self):
        """The scaled piece should be centered on the cursor position."""
        gui, window = _make_gui()
        mock_sprite = MagicMock()
        scale = floor(constants.SQ_HEIGHT * 1.1)
        cursor_x, cursor_y = 200, 300

        with patch.object(gui._sprites, 'get_sprite_from_code', return_value=mock_sprite):
            gui.draw_dragged_piece('pl', (cursor_x, cursor_y), (3, 3), (4, 4))
            # blit uses (y - scale/2, x - scale/2) where cursor_pos is (x, y)
            window.blit.assert_called_once_with(
                mock_sprite, (cursor_y - scale / 2, cursor_x - scale / 2))

    def test_normal_scale_on_start_square(self):
        """When cursor_sq == start_sq, piece should be drawn at normal scale."""
        gui, window = _make_gui()
        mock_sprite = MagicMock()
        sq = constants.SQ_HEIGHT

        with patch.object(gui._sprites, 'get_sprite_from_code', return_value=mock_sprite) as mock_get:
            gui.draw_dragged_piece('pl', (225, 225), (3, 3), (3, 3))
            mock_get.assert_called_once_with('pl', sq, sq)

    def test_start_square_blit_position(self):
        """On the start square, piece should blit at (col*SQ, row*SQ)."""
        gui, window = _make_gui()
        mock_sprite = MagicMock()
        sq = constants.SQ_HEIGHT

        with patch.object(gui._sprites, 'get_sprite_from_code', return_value=mock_sprite):
            gui.draw_dragged_piece('pl', (225, 225), (2, 5), (2, 5))
            # start_sq is (row=2, col=5), blit at (col*sq, row*sq) = (5*sq, 2*sq)
            window.blit.assert_called_once_with(mock_sprite, (5 * sq, 2 * sq))


class TestDrawPieces:
    """Test the board-wide piece drawing."""

    def test_draws_all_pieces_on_board(self):
        """draw_pieces should call draw_piece for every non-empty square."""
        gui, _ = _make_gui()
        board = GameState.empty()
        board.set_piece(0, 0, 'rd')
        board.set_piece(7, 4, 'kl')
        board.set_piece(6, 3, 'pl')

        with patch.object(gui, 'draw_piece') as mock_draw:
            gui.draw_pieces(board, 8, 8)
            assert mock_draw.call_count == 3
            mock_draw.assert_any_call('rd', 0, 0)
            mock_draw.assert_any_call('kl', 7, 4)
            mock_draw.assert_any_call('pl', 6, 3)

    def test_skips_empty_squares(self):
        """draw_pieces should not call draw_piece for empty squares."""
        gui, _ = _make_gui()
        board = GameState.empty()

        with patch.object(gui, 'draw_piece') as mock_draw:
            gui.draw_pieces(board, 8, 8)
            mock_draw.assert_not_called()


class TestDrawOverlays:
    """Test the overlay drawing composite method."""

    def test_draws_highlights_and_hints_when_dragging(self):
        """When a piece is being dragged, overlays should be rendered."""
        gui, _ = _make_gui()
        valid_moves = [(3, 3), (4, 4), (5, 5)]

        with patch.object(gui, 'draw_square_highlight') as mock_highlight:
            with patch.object(gui, 'draw_move_hint') as mock_hint:
                with patch.object(gui, 'draw_dragged_piece') as mock_drag:
                    gui.draw_overlays('pl', (6, 4), (5, 4),
                                      (400, 375), valid_moves)

                    # Should highlight start and cursor squares
                    assert mock_highlight.call_count == 2
                    mock_highlight.assert_any_call(6, 4)
                    mock_highlight.assert_any_call(5, 4)

                    # Should draw hints for all valid moves
                    assert mock_hint.call_count == 3
                    mock_hint.assert_any_call(3, 3)
                    mock_hint.assert_any_call(4, 4)
                    mock_hint.assert_any_call(5, 5)

                    # Should draw the dragged piece
                    mock_drag.assert_called_once_with(
                        'pl', (400, 375), (6, 4), (5, 4))

    def test_no_overlays_when_not_dragging(self):
        """When drag_piece is empty, no overlays should be drawn."""
        gui, _ = _make_gui()

        with patch.object(gui, 'draw_square_highlight') as mock_highlight:
            with patch.object(gui, 'draw_move_hint') as mock_hint:
                with patch.object(gui, 'draw_dragged_piece') as mock_drag:
                    gui.draw_overlays('', (0, 0), (0, 0), (0, 0), [])

                    mock_highlight.assert_not_called()
                    mock_hint.assert_not_called()
                    mock_drag.assert_not_called()

    def test_no_hints_when_no_valid_moves(self):
        """When dragging but no valid moves exist, hints should not be drawn."""
        gui, _ = _make_gui()

        with patch.object(gui, 'draw_square_highlight'):
            with patch.object(gui, 'draw_move_hint') as mock_hint:
                with patch.object(gui, 'draw_dragged_piece'):
                    gui.draw_overlays('pl', (6, 4), (5, 4), (400, 375), [])
                    mock_hint.assert_not_called()


class TestDrawSquareHighlight:
    """Test highlight overlay position calculation."""

    def test_position_calculation(self):
        """Highlight should be drawn at (SQ_HEIGHT*x, SQ_HEIGHT*y)."""
        gui, _ = _make_gui()
        sq = constants.SQ_HEIGHT

        with patch('pgchess.gui_manager.draw_solid_rect') as mock_rect:
            gui.draw_square_highlight(3, 5)
            mock_rect.assert_called_once_with(
                gui._window, sq, sq,
                sq * 3, sq * 5,
                constants.SQ_HIGHLIGHT_COLOR, constants.SQ_HIGHLIGHT_ALPHA,
            )


class TestDrawMoveHint:
    """Test move hint overlay position calculation."""

    def test_position_calculation(self):
        """Move hint should be drawn at (SQ_HEIGHT*x, SQ_HEIGHT*y)."""
        gui, _ = _make_gui()
        sq = constants.SQ_HEIGHT

        with patch('pgchess.gui_manager.draw_solid_circle') as mock_circle:
            gui.draw_move_hint(2, 6)
            mock_circle.assert_called_once_with(
                gui._window, sq, sq,
                sq / 7,
                sq * 2, sq * 6,
                constants.SQ_HINT_COLOR, constants.SQ_HINT_ALPHA,
            )
