"""In-game menu screens: start, pause, promotion, and game over."""
from typing import Callable, List

import pygame
import pygame_menu
from pygame_menu.themes import Theme

from pychess import constants
from .gui_utils import draw_board, draw_solid_rect, get_resource_path
from .sounds import Sounds

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
_ERROR_COLOR = (200, 50, 50, 255)


def _draw_overlay(window: pygame.Surface) -> None:
    """Draw a semi-transparent dark overlay behind a menu."""
    draw_solid_rect(window, constants.WINDOW_WIDTH,
                    constants.WINDOW_HEIGHT, 0, 0, _OVERLAY_COLOR, _OVERLAY_ALPHA)


def _on_select(sounds: Sounds) -> Callable:
    """Returns a callback that plays the menu-click sound when a widget is selected.

    :param sounds: The Sounds instance to use for playback
    :return: Callable suitable for use as a pygame_menu onselect handler
    """
    def _callback(selected: bool, _widget, _menu) -> None:
        if selected:
            sounds.play_menu_click()
    return _callback


def _on_confirm(sounds: Sounds, action: Callable) -> Callable:
    """Returns a callback to play the menu-confirm sound before invoking it.

    :param sounds: The Sounds instance to use for playback
    :param action: The original button action to wrap
    :return: Wrapped callable
    """
    def _callback() -> None:
        sounds.play_menu_confirm()
        action()
    return _callback


class Menu:
    """Base class for all menus, providing common drawing logic."""

    def __init__(self, sounds: Sounds) -> None:
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self._sounds = sounds

    def draw(self, window: pygame.Surface, events: List[pygame.event.Event]) -> None:
        """Render the menu overlay.

        :param window: The pygame surface to draw on
        :param events: Current frame's pygame events for menu interaction
        """
        _draw_overlay(window)
        self.menu.update(events)
        self.menu.draw(window)

    def _add_button(self, label: str, action: Callable, error_color: bool = False) -> None:
        """Add a button to the menu with the appropriate onselect handler and selection color."""
        selection_color = _ERROR_COLOR if error_color else self.menu.get_theme().selection_color
        self.menu.add.button(label, _on_confirm(self._sounds, action),
                             onselect=_on_select(self._sounds), selection_color=selection_color)


class StartMenu(Menu):
    """Main menu shown when the game launches."""

    def __init__(self, on_start_press: Callable, on_quit_press: Callable, sounds: Sounds) -> None:
        super().__init__(sounds)
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self.menu.add.image(get_resource_path(constants.PATH_LOGO), scale=(.6, .6), scale_smooth=True)
        self._add_button('Play', on_start_press)
        self._add_button('Quit', on_quit_press, True)

    def draw(self, window: pygame.Surface, events: List[pygame.event.Event]) -> None:
        """Render the start menu with the board background.

        :param window: The pygame surface to draw on
        :param events: Current frame's pygame events for menu interaction
        """
        draw_board(window)
        _draw_overlay(window)
        self.menu.update(events)
        self.menu.draw(window)


class PauseMenu(Menu):
    """Menu shown when the player presses Escape during a game."""

    def __init__(self, on_resume_press: Callable, on_resign_press: Callable, sounds: Sounds) -> None:
        super().__init__(sounds)
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self._add_button('Resume', on_resume_press)
        self._add_button('Resign', on_resign_press, True)


class PromotionMenu(Menu):
    """Menu shown when a pawn reaches the promotion rank."""

    def __init__(self, on_select: Callable[[str], None], sounds: Sounds) -> None:
        super().__init__(sounds)
        self.menu = pygame_menu.Menu('', 300, 300, theme=MENU_THEME, mouse_motion_selection=True)
        self.menu.add.label('Promote pawn to:')
        self._add_button('Queen', lambda: on_select('q'))
        self._add_button('Rook', lambda: on_select('r'))
        self._add_button('Bishop', lambda: on_select('b'))
        self._add_button('Knight', lambda: on_select('n'))


class GameOverMenu(Menu):
    """Menu shown when the game ends (checkmate or stalemate)."""

    def __init__(self, on_exit_press: Callable, sounds: Sounds) -> None:
        super().__init__(sounds)
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self._on_exit_press = on_exit_press

    def set_winner(self, white_wins: bool) -> None:
        """Configure the menu to display the winner.

        :param white_wins: True if white won, False if black won
        """
        self.menu.clear()
        self.menu.add.label('White wins' if white_wins else 'Black wins')
        self._add_button('Exit', self._on_exit_press)

    def set_draw(self) -> None:
        """Configure the menu to display a stalemate draw."""
        self.menu.clear()
        self.menu.add.label('Draw - Stalemate')
        self._add_button('Exit', self._on_exit_press)
