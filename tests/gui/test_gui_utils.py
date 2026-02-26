"""Tests for pgchess.gui.gui_utils: resource path resolution and draw helpers."""
import sys
from unittest.mock import patch, MagicMock, call

import pygame

from pgchess import constants
from pgchess.gui.gui_utils import get_resource_path, draw_board, draw_solid_rect, draw_solid_circle


class TestGetResourcePath:
    """Test the PyInstaller-aware resource path resolver."""

    def test_returns_raw_path_in_development(self):
        """Without _MEIPASS, the original path is returned unchanged."""
        if hasattr(sys, '_MEIPASS'):
            delattr(sys, '_MEIPASS')
        assert get_resource_path('assets/images/pgchess.png') == 'assets/images/pgchess.png'

    def test_returns_joined_path_when_frozen(self):
        """With _MEIPASS set, the path is joined to the temp directory."""
        with patch.object(sys, '_MEIPASS', '/tmp/_MEI12345', create=True):
            result = get_resource_path('assets/images/pgchess.png')
            assert result == '/tmp/_MEI12345/assets/images/pgchess.png'

    def test_empty_path(self):
        """An empty relative path returns the base dir (with trailing sep) when frozen."""
        with patch.object(sys, '_MEIPASS', '/tmp/_MEI12345', create=True):
            result = get_resource_path('')
            assert result == '/tmp/_MEI12345/'


class TestDrawBoard:
    """Test the chess board drawing function."""

    def test_draws_64_squares(self):
        """draw_board should call pygame.draw.rect exactly 64 times."""
        window = MagicMock(spec=pygame.Surface)
        with patch('pgchess.gui.gui_utils.pygame.draw.rect') as mock_rect:
            draw_board(window)
            assert mock_rect.call_count == 64

    def test_alternating_colors(self):
        """Light and dark squares should alternate in a checkerboard pattern."""
        window = MagicMock(spec=pygame.Surface)
        with patch('pgchess.gui.gui_utils.pygame.draw.rect') as mock_rect:
            draw_board(window)
            calls = mock_rect.call_args_list

            # (0,0) should be light, (0,1) dark, (1,0) dark, (1,1) light
            # draw_board iterates x (row) then y (col)
            # call index = x * 8 + y
            assert calls[0][0][1] == constants.SQ_LIGHT_COLOR   # (0,0) light
            assert calls[1][0][1] == constants.SQ_DARK_COLOR     # (0,1) dark
            assert calls[8][0][1] == constants.SQ_DARK_COLOR     # (1,0) dark
            assert calls[9][0][1] == constants.SQ_LIGHT_COLOR    # (1,1) light

    def test_square_positions(self):
        """Each square rect should be positioned at (SQ_HEIGHT*y, SQ_HEIGHT*x)."""
        window = MagicMock(spec=pygame.Surface)
        sq = constants.SQ_HEIGHT
        with patch('pgchess.gui.gui_utils.pygame.draw.rect') as mock_rect:
            draw_board(window)
            calls = mock_rect.call_args_list

            # First square (0,0): rect = (0, 0, SQ_HEIGHT, SQ_HEIGHT)
            assert calls[0][0][2] == (0, 0, sq, sq)
            # Square (0,1): rect = (SQ_HEIGHT, 0, SQ_HEIGHT, SQ_HEIGHT)
            assert calls[1][0][2] == (sq, 0, sq, sq)
            # Square (1,0): rect = (0, SQ_HEIGHT, SQ_HEIGHT, SQ_HEIGHT)
            assert calls[8][0][2] == (0, sq, sq, sq)


class TestDrawSolidRect:
    """Test the transparent rectangle drawing function."""

    def test_creates_surface_with_correct_size(self):
        """The temporary surface should match the requested dimensions."""
        window = MagicMock(spec=pygame.Surface)
        mock_surface = MagicMock()

        with patch('pgchess.gui.gui_utils.pygame.Surface', return_value=mock_surface) as mock_ctor:
            draw_solid_rect(window, 100, 50, 10, 20, (255, 0, 0), 128)
            mock_ctor.assert_called_once_with((100, 50))

    def test_sets_alpha_and_fills_color(self):
        """The surface should have alpha set and be filled with the color."""
        window = MagicMock(spec=pygame.Surface)
        mock_surface = MagicMock()

        with patch('pgchess.gui.gui_utils.pygame.Surface', return_value=mock_surface):
            draw_solid_rect(window, 100, 50, 10, 20, (255, 0, 0), 128)
            mock_surface.set_alpha.assert_called_once_with(128)
            mock_surface.fill.assert_called_once_with((255, 0, 0))

    def test_blits_at_swapped_position(self):
        """The blit destination should be (y_position, x_position) — swapped."""
        window = MagicMock(spec=pygame.Surface)
        mock_surface = MagicMock()

        with patch('pgchess.gui.gui_utils.pygame.Surface', return_value=mock_surface):
            draw_solid_rect(window, 100, 50, 10, 20, (255, 0, 0))
            window.blit.assert_called_once_with(mock_surface, (20, 10))

    def test_default_alpha_is_opaque(self):
        """When no alpha is provided, it should default to 255."""
        window = MagicMock(spec=pygame.Surface)
        mock_surface = MagicMock()

        with patch('pgchess.gui.gui_utils.pygame.Surface', return_value=mock_surface):
            draw_solid_rect(window, 100, 50, 10, 20, (255, 0, 0))
            mock_surface.set_alpha.assert_called_once_with(255)


class TestDrawSolidCircle:
    """Test the transparent circle drawing function."""

    def test_creates_surface_with_correct_size(self):
        """The bounding surface should match the requested dimensions."""
        window = MagicMock(spec=pygame.Surface)
        mock_surface = MagicMock()

        with patch('pgchess.gui.gui_utils.pygame.Surface', return_value=mock_surface):
            with patch('pgchess.gui.gui_utils.pygame.draw.circle') as mock_circle:
                draw_solid_circle(window, 80, 80, 10.0, 30, 40, (0, 255, 0), 200)
                mock_circle.assert_called_once_with(mock_surface, (0, 255, 0, 200), (40.0, 40.0), 10.0)

    def test_circle_centered_in_surface(self):
        """The circle center should be at (width/2, height/2)."""
        window = MagicMock(spec=pygame.Surface)
        mock_surface = MagicMock()

        with patch('pgchess.gui.gui_utils.pygame.Surface', return_value=mock_surface):
            with patch('pgchess.gui.gui_utils.pygame.draw.circle') as mock_circle:
                draw_solid_circle(window, 60, 40, 5.0, 0, 0, (0, 0, 0))
                center_arg = mock_circle.call_args[0][2]
                assert center_arg == (30.0, 20.0)

    def test_blits_at_swapped_position(self):
        """The blit destination should be (y_position, x_position) — swapped."""
        window = MagicMock(spec=pygame.Surface)
        mock_surface = MagicMock()

        with patch('pgchess.gui.gui_utils.pygame.Surface', return_value=mock_surface):
            with patch('pgchess.gui.gui_utils.pygame.draw.circle'):
                draw_solid_circle(window, 80, 80, 10.0, 30, 40, (0, 255, 0))
                window.blit.assert_called_once_with(mock_surface, (40, 30))
