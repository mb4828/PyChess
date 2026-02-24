"""Main game manager for PGChess. Manages the application loop, menus, and game mode transitions."""
import logging
from enum import Enum
from typing import Optional

import pygame

from pgchess import constants
from pgchess.game.game import Game
from pgchess.game.pvc_game import PVCGame
from pgchess.game.pvp_game import PVPGame
from pgchess.gui.gui_utils import get_resource_path
from pgchess.gui.menus import StartMenu, PauseMenu, GameOverMenu, PromotionMenu
from pgchess.gui.sounds import Sounds

logger = logging.getLogger(__name__)


class AppState(Enum):
    """Possible states of the PGChess application."""
    START = 1
    PAUSE = 2
    PLAYER_MOVE = 3
    GAME_OVER = 4
    PROMOTION = 5


class GameManager:
    """Manages the application loop, menus, and transitions between game modes.

    Instantiating this class initialises pygame and immediately enters the main loop.
    To support additional game modes (e.g. PVC), add a ``start_<mode>_game`` method
    that sets ``self._game`` to the appropriate :class:`~pychess.game.game.Game` subclass
    and transitions ``self._app_state`` to the matching :class:`AppState`.
    """

    def __init__(self) -> None:
        pygame.init()

        self._window: pygame.Surface  # assigned by _init_display
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._app_state: AppState = AppState.START
        self._running: bool = True
        self._game: Optional[Game] = None
        self._sounds: Sounds = Sounds()

        self._init_display()
        self._init_menus()

    def run(self) -> None:
        """Run the main game loop, processing events and rendering each frame."""
        while self._running:
            events = pygame.event.get()
            for event in events:
                self._handle_event(event)

            self._draw(events)
            pygame.display.update()
            self._clock.tick(60)

        pygame.quit()

    def _init_display(self) -> None:
        """Initialise the pygame display: create the window, caption, and icon.

        Called once from ``__init__`` before the main loop starts.
        """
        self._window = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
        pygame.display.set_caption('PGChess')
        pygame.display.set_icon(
            pygame.image.load(get_resource_path(constants.PATH_ICON)))

    def _init_menus(self) -> None:
        """Instantiate all menu objects and wire their callbacks.

        Called once from ``__init__`` after the display is ready.
        """
        self._start_menu = StartMenu(self._start_pvp_game, self._start_pvc_game, self._quit_game, self._sounds)
        self._pause_menu = PauseMenu(self._resume_game, self._resign_game, self._sounds)
        self._game_over_menu = GameOverMenu(self._resign_game, self._sounds)
        self._promotion_menu = PromotionMenu(self._on_promotion_select, self._sounds)

    def _start_pvp_game(self) -> None:
        """Initialise and start a new player-vs-player game."""
        self._game = PVPGame(self._window, self._sounds)
        self._app_state = AppState.PLAYER_MOVE

    def _start_pvc_game(self) -> None:
        """Initialise and start a new player-vs-computer game."""
        self._game = PVCGame(self._window, self._sounds)
        self._app_state = AppState.PLAYER_MOVE

    def _resume_game(self) -> None:
        """Resume the current game from the pause menu."""
        self._app_state = AppState.PLAYER_MOVE

    def _resign_game(self) -> None:
        """Return to the start menu, abandoning the current game."""
        self._app_state = AppState.START

    def _quit_game(self) -> None:
        """Signal the main loop to exit."""
        self._running = False

    def _on_promotion_select(self, piece_type: str) -> None:
        """Handle pawn promotion piece selection from the promotion menu.

        :param piece_type: The piece type character ('q', 'r', 'b', or 'n')
        """
        if self._game:
            self._game.complete_promotion(piece_type)
            self._app_state = AppState.PLAYER_MOVE

    def _handle_event(self, event: pygame.event.Event) -> None:
        """Dispatch a single pygame event to the appropriate handler.

        :param event: The pygame event to handle
        """
        if event.type == pygame.QUIT:
            self._quit_game()
        elif event.type == pygame.KEYDOWN and event.key == pygame.locals.K_ESCAPE and self._app_state == AppState.PLAYER_MOVE:
            self._app_state = AppState.PAUSE
        elif event.type == constants.EVENT_WHITE_WINS:
            self._app_state = AppState.GAME_OVER
            self._game_over_menu.set_winner(True)
        elif event.type == constants.EVENT_BLACK_WINS:
            self._app_state = AppState.GAME_OVER
            self._game_over_menu.set_winner(False)
        elif event.type == constants.EVENT_DRAW:
            self._app_state = AppState.GAME_OVER
            self._game_over_menu.set_draw()
        elif event.type == constants.EVENT_PROMOTION:
            self._app_state = AppState.PROMOTION
        elif self._game and self._app_state == AppState.PLAYER_MOVE:
            self._game.handle_event(event)

    def _draw(self, events: list) -> None:
        """Render the current frame based on application state.

        :param events: The pygame events for the current frame, passed to menu widgets
        """
        self._window.fill(constants.WINDOW_COLOR)
        if self._game:
            self._game.draw()

        state_menu_map = {
            AppState.START: self._start_menu,
            AppState.PAUSE: self._pause_menu,
            AppState.GAME_OVER: self._game_over_menu,
            AppState.PROMOTION: self._promotion_menu,
        }
        menu = state_menu_map.get(self._app_state)
        if menu:
            menu.draw(self._window, events)
