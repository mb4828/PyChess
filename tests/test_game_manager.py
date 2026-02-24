"""Tests for pgchess.game_manager.GameManager."""
from unittest.mock import MagicMock, patch

import pygame
import pytest

from pgchess import constants
from pgchess.game_manager import AppState, GameManager


@pytest.fixture
def manager():
    """Create a GameManager with all pygame and menu dependencies mocked."""
    with patch('pgchess.game_manager.pygame.init'), \
         patch('pgchess.game_manager.pygame.quit'), \
         patch('pgchess.game_manager.pygame.display') as mock_display, \
         patch('pgchess.game_manager.pygame.image'), \
         patch('pgchess.game_manager.pygame.time') as mock_time, \
         patch('pgchess.game_manager.get_resource_path', return_value='icon.png'), \
         patch('pgchess.game_manager.StartMenu'), \
         patch('pgchess.game_manager.PauseMenu'), \
         patch('pgchess.game_manager.GameOverMenu'), \
         patch('pgchess.game_manager.PromotionMenu'), \
         patch('pgchess.game_manager.Sounds'):
        mock_display.set_mode.return_value = MagicMock()
        mock_time.Clock.return_value = MagicMock()
        yield GameManager()


def _event(event_type, **attrs):
    """Build a mock pygame event with the given type and attributes."""
    e = MagicMock()
    e.type = event_type
    for k, v in attrs.items():
        setattr(e, k, v)
    return e


class TestStateTransitions:
    def test_initial_state_is_start(self, manager):
        """The application should open on the start menu."""
        assert manager._app_state == AppState.START

    def test_start_pvp_game_sets_player_move_state(self, manager):
        """Starting a PVP game should immediately enter the playing state."""
        with patch('pgchess.game_manager.PVPGame'):
            manager._start_pvp_game()
        assert manager._app_state == AppState.PLAYER_MOVE

    def test_start_pvp_game_creates_pvp_game_instance(self, manager):
        """Starting a PVP game should create a PVPGame and assign it."""
        with patch('pgchess.game_manager.PVPGame') as mock_pvp:
            manager._start_pvp_game()
        mock_pvp.assert_called_once()
        assert manager._game is mock_pvp.return_value

    def test_start_pvc_game_sets_player_move_state(self, manager):
        """Starting a PVC game should immediately enter the playing state."""
        with patch('pgchess.game_manager.PVCGame'):
            manager._start_pvc_game()
        assert manager._app_state == AppState.PLAYER_MOVE

    def test_start_pvc_game_creates_pvc_game_instance(self, manager):
        """Starting a PVC game should create a PVCGame and assign it."""
        with patch('pgchess.game_manager.PVCGame') as mock_pvc:
            manager._start_pvc_game()
        mock_pvc.assert_called_once()
        assert manager._game is mock_pvc.return_value

    def test_resume_game_sets_player_move_state(self, manager):
        """Resuming from pause should return to the playing state."""
        manager._app_state = AppState.PAUSE
        manager._resume_game()
        assert manager._app_state == AppState.PLAYER_MOVE

    def test_resign_game_returns_to_start(self, manager):
        """Resigning should discard the current game and show the start menu."""
        manager._app_state = AppState.PLAYER_MOVE
        manager._resign_game()
        assert manager._app_state == AppState.START

    def test_quit_game_stops_main_loop(self, manager):
        """Quitting should signal the main loop to exit."""
        manager._quit_game()
        assert manager._running is False


class TestHandleEvent:
    def test_quit_event_stops_loop(self, manager):
        """A QUIT event should stop the main loop."""
        manager._handle_event(_event(pygame.QUIT))
        assert manager._running is False

    def test_escape_during_player_move_pauses_game(self, manager):
        """Pressing Escape while playing should open the pause menu."""
        manager._app_state = AppState.PLAYER_MOVE
        manager._handle_event(_event(pygame.KEYDOWN, key=pygame.locals.K_ESCAPE))
        assert manager._app_state == AppState.PAUSE

    def test_escape_ignored_outside_player_move(self, manager):
        """Pressing Escape while not playing should not change state."""
        manager._app_state = AppState.PAUSE
        manager._handle_event(_event(pygame.KEYDOWN, key=pygame.locals.K_ESCAPE))
        assert manager._app_state == AppState.PAUSE

    def test_white_wins_event_sets_game_over(self, manager):
        """EVENT_WHITE_WINS should transition to the game-over screen."""
        manager._handle_event(_event(constants.EVENT_WHITE_WINS))
        assert manager._app_state == AppState.GAME_OVER

    def test_white_wins_event_marks_white_as_winner(self, manager):
        """EVENT_WHITE_WINS should pass True to the game-over menu."""
        manager._handle_event(_event(constants.EVENT_WHITE_WINS))
        manager._game_over_menu.set_winner.assert_called_once_with(True)

    def test_black_wins_event_sets_game_over(self, manager):
        """EVENT_BLACK_WINS should transition to the game-over screen."""
        manager._handle_event(_event(constants.EVENT_BLACK_WINS))
        assert manager._app_state == AppState.GAME_OVER

    def test_black_wins_event_marks_black_as_winner(self, manager):
        """EVENT_BLACK_WINS should pass False to the game-over menu."""
        manager._handle_event(_event(constants.EVENT_BLACK_WINS))
        manager._game_over_menu.set_winner.assert_called_once_with(False)

    def test_draw_event_sets_game_over(self, manager):
        """EVENT_DRAW should transition to the game-over screen."""
        manager._handle_event(_event(constants.EVENT_DRAW))
        assert manager._app_state == AppState.GAME_OVER

    def test_draw_event_calls_set_draw(self, manager):
        """EVENT_DRAW should mark the game-over menu as a draw, not a win."""
        manager._handle_event(_event(constants.EVENT_DRAW))
        manager._game_over_menu.set_draw.assert_called_once()

    def test_promotion_event_sets_promotion_state(self, manager):
        """EVENT_PROMOTION should open the promotion piece-selection menu."""
        manager._handle_event(_event(constants.EVENT_PROMOTION))
        assert manager._app_state == AppState.PROMOTION

    def test_mouse_event_during_player_move_forwarded_to_game(self, manager):
        """Mouse events during active play should be passed to the game object."""
        mock_game = MagicMock()
        manager._game = mock_game
        manager._app_state = AppState.PLAYER_MOVE
        e = _event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
        manager._handle_event(e)
        mock_game.handle_event.assert_called_once_with(e)

    def test_mouse_event_during_pause_not_forwarded(self, manager):
        """Mouse events should be ignored while the pause menu is open."""
        mock_game = MagicMock()
        manager._game = mock_game
        manager._app_state = AppState.PAUSE
        manager._handle_event(_event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100)))
        mock_game.handle_event.assert_not_called()


class TestOnPromotionSelect:
    def test_calls_complete_promotion_on_game(self, manager):
        """Selecting a promotion piece should delegate to the game object."""
        mock_game = MagicMock()
        manager._game = mock_game
        manager._on_promotion_select('q')
        mock_game.complete_promotion.assert_called_once_with('q')

    def test_returns_to_player_move_state(self, manager):
        """After promotion, play should resume."""
        manager._game = MagicMock()
        manager._app_state = AppState.PROMOTION
        manager._on_promotion_select('q')
        assert manager._app_state == AppState.PLAYER_MOVE

    def test_no_op_when_no_game(self, manager):
        """Promotion select with no active game should not change state."""
        manager._game = None
        manager._app_state = AppState.START
        manager._on_promotion_select('q')
        assert manager._app_state == AppState.START


class TestDraw:
    def test_draws_start_menu_in_start_state(self, manager):
        """The start menu should be rendered when the app is on the start screen."""
        manager._app_state = AppState.START
        manager._game = None
        manager._draw([])
        manager._start_menu.draw.assert_called_once()

    def test_draws_pause_menu_in_pause_state(self, manager):
        """The pause menu should be rendered when the game is paused."""
        manager._app_state = AppState.PAUSE
        manager._game = None
        manager._draw([])
        manager._pause_menu.draw.assert_called_once()

    def test_draws_game_over_menu_in_game_over_state(self, manager):
        """The game-over menu should be rendered at end of game."""
        manager._app_state = AppState.GAME_OVER
        manager._game = None
        manager._draw([])
        manager._game_over_menu.draw.assert_called_once()

    def test_draws_promotion_menu_in_promotion_state(self, manager):
        """The promotion menu should be rendered when a pawn reaches the back rank."""
        manager._app_state = AppState.PROMOTION
        manager._game = None
        manager._draw([])
        manager._promotion_menu.draw.assert_called_once()

    def test_no_menu_drawn_in_player_move_state(self, manager):
        """No overlay menu should appear during active gameplay."""
        manager._app_state = AppState.PLAYER_MOVE
        manager._game = None
        manager._draw([])
        manager._start_menu.draw.assert_not_called()
        manager._pause_menu.draw.assert_not_called()
        manager._game_over_menu.draw.assert_not_called()
        manager._promotion_menu.draw.assert_not_called()

    def test_calls_game_draw_when_game_exists(self, manager):
        """The board and pieces should be rendered whenever a game is active."""
        mock_game = MagicMock()
        manager._game = mock_game
        manager._app_state = AppState.PLAYER_MOVE
        manager._draw([])
        mock_game.draw.assert_called_once()

    def test_skips_game_draw_when_no_game(self, manager):
        """No board rendering should occur before a game has started."""
        manager._game = None
        manager._app_state = AppState.START
        manager._draw([])
        # Verified implicitly — no AttributeError and start menu is shown
        manager._start_menu.draw.assert_called_once()
