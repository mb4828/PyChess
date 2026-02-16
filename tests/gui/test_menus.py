"""Tests for pychess.gui.menus: menu construction and configuration."""
import os
from unittest.mock import patch, MagicMock, call

import pygame
import pygame_menu

from pychess import constants
from pychess.gui.menus import StartMenu, PauseMenu, PromotionMenu, GameOverMenu, _draw_overlay


class TestDrawOverlay:
    """Test the semi-transparent menu overlay helper."""

    def test_draws_full_window_overlay(self):
        """_draw_overlay should draw a rect covering the entire window."""
        window = MagicMock(spec=pygame.Surface)

        with patch('pychess.gui.menus.draw_solid_rect') as mock_rect:
            _draw_overlay(window)
            mock_rect.assert_called_once_with(
                window,
                constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT,
                0, 0,
                (0, 0, 0), 85,
            )


class TestStartMenu:
    """Test the start menu construction."""

    @patch('pychess.gui.menus.get_resource_path', side_effect=lambda p: p)
    def test_has_play_and_quit_buttons(self, _mock_path):
        """StartMenu should have Play and Quit buttons."""
        on_start = MagicMock()
        on_quit = MagicMock()
        menu = StartMenu(on_start, on_quit)

        widgets = menu.menu.get_widgets()
        labels = [w.get_title() for w in widgets if hasattr(w, 'get_title')]
        assert 'Play' in labels
        assert 'Quit' in labels

    @patch('pychess.gui.menus.get_resource_path', side_effect=lambda p: p)
    def test_draw_renders_board_overlay_and_menu(self, _mock_path):
        """StartMenu.draw should render board background, overlay, and menu."""
        menu = StartMenu(MagicMock(), MagicMock())
        window = MagicMock(spec=pygame.Surface)
        events = []

        with patch('pychess.gui.menus.draw_board') as mock_board:
            with patch('pychess.gui.menus._draw_overlay') as mock_overlay:
                with patch.object(menu.menu, 'update') as mock_update:
                    with patch.object(menu.menu, 'draw') as mock_draw:
                        menu.draw(window, events)
                        mock_board.assert_called_once_with(window)
                        mock_overlay.assert_called_once_with(window)
                        mock_update.assert_called_once_with(events)
                        mock_draw.assert_called_once_with(window)


class TestPauseMenu:
    """Test the pause menu construction."""

    def test_has_resume_and_resign_buttons(self):
        """PauseMenu should have Resume and Resign buttons."""
        menu = PauseMenu(MagicMock(), MagicMock())

        widgets = menu.menu.get_widgets()
        labels = [w.get_title() for w in widgets if hasattr(w, 'get_title')]
        assert 'Resume' in labels
        assert 'Resign' in labels

    def test_draw_renders_overlay_and_menu(self):
        """PauseMenu.draw should render the overlay and menu widgets."""
        menu = PauseMenu(MagicMock(), MagicMock())
        window = MagicMock(spec=pygame.Surface)

        with patch('pychess.gui.menus._draw_overlay') as mock_overlay:
            with patch.object(menu.menu, 'update'):
                with patch.object(menu.menu, 'draw'):
                    menu.draw(window, [])
                    mock_overlay.assert_called_once_with(window)


class TestPromotionMenu:
    """Test the promotion selection menu."""

    def test_has_four_piece_buttons(self):
        """PromotionMenu should have Queen, Rook, Bishop, Knight buttons."""
        menu = PromotionMenu(MagicMock())

        widgets = menu.menu.get_widgets()
        labels = [w.get_title() for w in widgets if hasattr(w, 'get_title')]
        assert 'Queen' in labels
        assert 'Rook' in labels
        assert 'Bishop' in labels
        assert 'Knight' in labels

    def test_has_label(self):
        """PromotionMenu should have a 'Promote pawn to:' label."""
        menu = PromotionMenu(MagicMock())

        widgets = menu.menu.get_widgets()
        labels = [w.get_title() for w in widgets if hasattr(w, 'get_title')]
        assert 'Promote pawn to:' in labels


class TestGameOverMenu:
    """Test the game over menu configuration."""

    def test_set_winner_white(self):
        """set_winner(True) should display 'White wins'."""
        menu = GameOverMenu(MagicMock())
        menu.set_winner(True)

        widgets = menu.menu.get_widgets()
        labels = [w.get_title() for w in widgets if hasattr(w, 'get_title')]
        assert 'White wins' in labels
        assert 'Exit' in labels

    def test_set_winner_black(self):
        """set_winner(False) should display 'Black wins'."""
        menu = GameOverMenu(MagicMock())
        menu.set_winner(False)

        widgets = menu.menu.get_widgets()
        labels = [w.get_title() for w in widgets if hasattr(w, 'get_title')]
        assert 'Black wins' in labels

    def test_set_draw(self):
        """set_draw should display 'Draw - Stalemate'."""
        menu = GameOverMenu(MagicMock())
        menu.set_draw()

        widgets = menu.menu.get_widgets()
        labels = [w.get_title() for w in widgets if hasattr(w, 'get_title')]
        assert 'Draw - Stalemate' in labels
        assert 'Exit' in labels

    def test_set_winner_clears_previous(self):
        """Calling set_winner after set_draw should replace the content."""
        menu = GameOverMenu(MagicMock())
        menu.set_draw()
        menu.set_winner(True)

        widgets = menu.menu.get_widgets()
        labels = [w.get_title() for w in widgets if hasattr(w, 'get_title')]
        assert 'White wins' in labels
        assert 'Draw - Stalemate' not in labels
