"""In-game menu screens: start, pause, promotion, and game over."""
from typing import Callable, List

import pygame
import pygame_menu
from pygame_menu.themes import Theme

from pychess import constants
from .gui_utils import draw_board, draw_solid_rect, get_resource_path

MENU_THEME = Theme(
    background_color=(255, 255, 255, 255),
    title_close_button=False,
    selection_color=(110, 148, 205, 255),
    title_background_color=(110, 148, 205, 255),
    title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
    title_font_size=1,
    title_font_shadow=False,
    widget_font=pygame_menu.font.FONT_OPEN_SANS,
    widget_font_color=(0, 0, 0, 255),
)

_OVERLAY_COLOR = (0, 0, 0)
_OVERLAY_ALPHA = 85


def _draw_overlay(window: pygame.Surface) -> None:
    """Draw a semi-transparent dark overlay behind a menu."""
    draw_solid_rect(window, constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, 0, 0, _OVERLAY_COLOR, _OVERLAY_ALPHA)


class StartMenu:
    """Main menu shown when the game launches."""

    def __init__(self, on_start_press: Callable, on_quit_press: Callable) -> None:
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self.menu.add.image(get_resource_path(constants.PATH_LOGO), scale=(.6, .6), scale_smooth=True)
        self.menu.add.button('Play', on_start_press)
        self.menu.add.button('Quit', on_quit_press)

    def draw(self, window: pygame.Surface, events: List[pygame.event.Event]) -> None:
        """Render the start menu with the board background.

        :param window: The pygame surface to draw on
        :param events: Current frame's pygame events for menu interaction
        """
        draw_board(window)
        _draw_overlay(window)
        self.menu.update(events)
        self.menu.draw(window)


class PauseMenu:
    """Menu shown when the player presses Escape during a game."""

    def __init__(self, on_resume_press: Callable, on_resign_press: Callable) -> None:
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self.menu.add.button('Resume', on_resume_press)
        self.menu.add.button('Resign', on_resign_press)

    def draw(self, window: pygame.Surface, events: List[pygame.event.Event]) -> None:
        """Render the pause menu overlay.

        :param window: The pygame surface to draw on
        :param events: Current frame's pygame events for menu interaction
        """
        _draw_overlay(window)
        self.menu.update(events)
        self.menu.draw(window)


class PromotionMenu:
    """Menu shown when a pawn reaches the promotion rank."""

    def __init__(self, on_select: Callable[[str], None]) -> None:
        self.menu = pygame_menu.Menu('', 300, 300, theme=MENU_THEME, mouse_motion_selection=True)
        self.menu.add.label('Promote pawn to:')
        self.menu.add.button('Queen', lambda: on_select('q'))
        self.menu.add.button('Rook', lambda: on_select('r'))
        self.menu.add.button('Bishop', lambda: on_select('b'))
        self.menu.add.button('Knight', lambda: on_select('n'))

    def draw(self, window: pygame.Surface, events: List[pygame.event.Event]) -> None:
        """Render the promotion selection menu overlay.

        :param window: The pygame surface to draw on
        :param events: Current frame's pygame events for menu interaction
        """
        _draw_overlay(window)
        self.menu.update(events)
        self.menu.draw(window)


class GameOverMenu:
    """Menu shown when the game ends (checkmate or stalemate)."""

    def __init__(self, on_exit_press: Callable) -> None:
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self.on_exit_press = on_exit_press

    def set_winner(self, white_wins: bool) -> None:
        """Configure the menu to display the winner.

        :param white_wins: True if white won, False if black won
        """
        self.menu.clear()
        self.menu.add.label('White wins' if white_wins else 'Black wins')
        self.menu.add.button('Exit', self.on_exit_press)

    def set_draw(self) -> None:
        """Configure the menu to display a stalemate draw."""
        self.menu.clear()
        self.menu.add.label('Draw - Stalemate')
        self.menu.add.button('Exit', self.on_exit_press)

    def draw(self, window: pygame.Surface, events: List[pygame.event.Event]) -> None:
        """Render the game over menu overlay.

        :param window: The pygame surface to draw on
        :param events: Current frame's pygame events for menu interaction
        """
        _draw_overlay(window)
        self.menu.update(events)
        self.menu.draw(window)
