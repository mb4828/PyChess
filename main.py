"""PyChess application entry point and main game loop."""
import logging
from enum import Enum
from typing import Optional

import pygame

from pychess import constants
from pychess.gui.gui_utils import get_resource_path
from pychess.gui.menus import StartMenu, PauseMenu, GameOverMenu, PromotionMenu
from pychess.game.pvp import PVPGame

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Possible states of the PyChess application."""

    START = 1
    PAUSE = 2
    PVP = 3
    GAME_OVER = 4
    PROMOTION = 5


class PyChess:
    """Main application class that manages the game loop, menus, and state transitions."""

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()

        self.window: pygame.Surface = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.game_state: GameState = GameState.START
        self.running: bool = True
        self.dragging: bool = False
        self.game: Optional[PVPGame] = None

        pygame.display.set_caption(f'PyChess v{constants.VERSION}')
        pygame.display.set_icon(pygame.image.load(get_resource_path(constants.PATH_KL)))

        self.start_menu = StartMenu(self.start_pvp_game, self.quit_game)
        self.pause_menu = PauseMenu(
            lambda: self.set_game_state(GameState.PVP),
            lambda: self.set_game_state(GameState.START),
        )
        self.game_over_menu = GameOverMenu(lambda: self.set_game_state(GameState.START))
        self.promotion_menu = PromotionMenu(self.on_promotion_select)

        self.main()

    def set_game_state(self, state: GameState) -> None:
        """Set the current game state.

        :param state: The new game state
        """
        self.game_state = state

    def start_pvp_game(self) -> None:
        """Initialize and start a new player-vs-player game."""
        self.game = PVPGame(self.window)
        self.game_state = GameState.PVP

    def quit_game(self) -> None:
        """Signal the main loop to exit."""
        self.running = False

    def on_promotion_select(self, piece_type: str) -> None:
        """Handle pawn promotion piece selection from the promotion menu.

        :param piece_type: The piece type character ('q', 'r', 'b', or 'n')
        """
        if self.game:
            self.game.complete_promotion(piece_type)
            self.game_state = GameState.PVP

    def main(self) -> None:
        """Run the main game loop, processing events and rendering each frame."""
        while self.running:
            events = pygame.event.get()
            for event in events:
                self._handle_event(event)

            self._draw(events)
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()
        pygame.mixer.quit()

    def _handle_event(self, event: pygame.event.Event) -> None:
        """Dispatch a single pygame event to the appropriate handler."""
        if event.type == pygame.QUIT:
            self.quit_game()
        elif event.type == pygame.KEYDOWN and event.key == pygame.locals.K_ESCAPE and self.game_state == GameState.PVP:
            self.game_state = GameState.PAUSE
        elif (self.game and event.type == pygame.MOUSEBUTTONDOWN
              and event.button == 1 and self.game_state == GameState.PVP):
            self.dragging = True
            y, x = event.pos
            self.game.drag_start(x, y)
        elif self.game and event.type == pygame.MOUSEMOTION and self.dragging and self.game_state == GameState.PVP:
            y, x = event.pos
            self.game.drag_continue(x, y)
        elif (self.game and event.type == pygame.MOUSEBUTTONUP
              and event.button == 1 and self.game_state == GameState.PVP):
            self.dragging = False
            self.game.drag_stop()
        elif event.type == constants.EVENT_WHITE_WINS:
            self.game_state = GameState.GAME_OVER
            self.game_over_menu.set_winner(True)
        elif event.type == constants.EVENT_BLACK_WINS:
            self.game_state = GameState.GAME_OVER
            self.game_over_menu.set_winner(False)
        elif event.type == constants.EVENT_DRAW:
            self.game_state = GameState.GAME_OVER
            self.game_over_menu.set_draw()
        elif event.type == constants.EVENT_PROMOTION:
            self.game_state = GameState.PROMOTION

    def _draw(self, events: list) -> None:
        """Render the current frame based on game state.

        :param events: The pygame events for the current frame, passed to menu widgets
        """
        self.window.fill(constants.WINDOW_COLOR)
        if self.game:
            self.game.draw()

        state_menu_map = {
            GameState.START: self.start_menu,
            GameState.PAUSE: self.pause_menu,
            GameState.GAME_OVER: self.game_over_menu,
            GameState.PROMOTION: self.promotion_menu,
        }
        menu = state_menu_map.get(self.game_state)
        if menu:
            menu.draw(self.window, events)


if __name__ == '__main__':
    PyChess()
