"""Tests for pgchess.game.pvp_game.PVPGame."""
from unittest.mock import MagicMock, patch

import pygame
import pytest

from pgchess.game.game import Game
from pgchess.game.pvp_game import PVPGame
from pgchess.gui.sounds import Sounds


@pytest.fixture
def pvp_game():
    """Create a PVPGame with a mocked GUIManager."""
    window = MagicMock(spec=pygame.Surface)
    sounds = MagicMock(spec=Sounds)
    with patch('pgchess.game.game.GUIManager') as mock_gui_cls:
        mock_gui = MagicMock()
        mock_gui.sounds = MagicMock()
        mock_gui_cls.return_value = mock_gui
        g = PVPGame(window, sounds)
    return g


class TestPVPGame:
    def test_is_subclass_of_game(self):
        """PVPGame should extend Game with no additional logic."""
        assert issubclass(PVPGame, Game)

    def test_starts_with_white_turn(self, pvp_game):
        """White should move first at game start."""
        assert pvp_game.state.current_color() == 'l'

    def test_game_start_sound_plays_on_init(self, pvp_game):
        """The game-start sound should fire exactly once when a new game is created."""
        pvp_game.gui.sounds.play_game_start.assert_called_once()

    def test_no_drag_piece_initially(self, pvp_game):
        """No piece should be in the drag state at the start of a game."""
        assert pvp_game.drag_piece == ''

    def test_no_pending_promotion_initially(self, pvp_game):
        """There should be no pending promotion at the start of a game."""
        assert pvp_game.pending_promotion is None
