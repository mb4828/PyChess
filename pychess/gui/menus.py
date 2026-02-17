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
    """Return an onselect callback that plays the menu-click sound when a widget is selected.

    :param sounds: The Sounds instance to use for playback
    :return: Callable suitable for use as a pygame_menu onselect handler
    """
    def _callback(selected: bool, _widget, _menu) -> None:
        if selected:
            sounds.play_menu_click()
    return _callback


def _with_confirm(sounds: Sounds, action: Callable) -> Callable:
    """Wrap an action callback to play the menu-confirm sound before invoking it.

    :param sounds: The Sounds instance to use for playback
    :param action: The original button action to wrap
    :return: Wrapped callable
    """
    def _callback() -> None:
        sounds.play_menu_confirm()
        action()
    return _callback


def _with_game_over(sounds: Sounds, action: Callable) -> Callable:
    """Wrap an action callback to play the game-over sound before invoking it.

    :param sounds: The Sounds instance to use for playback
    :param action: The original button action to wrap
    :return: Wrapped callable
    """
    def _callback() -> None:
        sounds.play_game_over()
        action()
    return _callback


class StartMenu:
    """Main menu shown when the game launches."""

    def __init__(self, on_start_press: Callable, on_quit_press: Callable, sounds: Sounds) -> None:
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self.menu.add.image(get_resource_path(constants.PATH_LOGO), scale=(.6, .6), scale_smooth=True)
        on_select = _on_select(sounds)
        self.menu.add.button('Play', _with_confirm(sounds, on_start_press), onselect=on_select)
        self.menu.add.button('Quit', _with_confirm(sounds, on_quit_press),
                             onselect=on_select, selection_color=_ERROR_COLOR)

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

    def __init__(self, on_resume_press: Callable, on_resign_press: Callable, sounds: Sounds) -> None:
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        on_select = _on_select(sounds)
        self.menu.add.button('Resume', _with_confirm(sounds, on_resume_press), onselect=on_select)
        self.menu.add.button('Resign', _with_game_over(sounds, on_resign_press),
                             onselect=on_select, selection_color=_ERROR_COLOR)

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

    def __init__(self, on_select: Callable[[str], None], sounds: Sounds) -> None:
        self.menu = pygame_menu.Menu('', 300, 300, theme=MENU_THEME, mouse_motion_selection=True)
        on_sel = _on_select(sounds)
        self.menu.add.label('Promote pawn to:')
        self.menu.add.button('Queen', _with_confirm(sounds, lambda: on_select('q')), onselect=on_sel)
        self.menu.add.button('Rook', _with_confirm(sounds, lambda: on_select('r')), onselect=on_sel)
        self.menu.add.button('Bishop', _with_confirm(sounds, lambda: on_select('b')), onselect=on_sel)
        self.menu.add.button('Knight', _with_confirm(sounds, lambda: on_select('n')), onselect=on_sel)

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

    def __init__(self, on_exit_press: Callable, sounds: Sounds) -> None:
        self.menu = pygame_menu.Menu('', 300, 250, theme=MENU_THEME, mouse_motion_selection=True)
        self._on_exit_press = _with_confirm(sounds, on_exit_press)
        self._on_select = _on_select(sounds)

    def set_winner(self, white_wins: bool) -> None:
        """Configure the menu to display the winner.

        :param white_wins: True if white won, False if black won
        """
        self.menu.clear()
        self.menu.add.label('White wins' if white_wins else 'Black wins')
        self.menu.add.button('Exit', self._on_exit_press,
                             onselect=self._on_select)

    def set_draw(self) -> None:
        """Configure the menu to display a stalemate draw."""
        self.menu.clear()
        self.menu.add.label('Draw - Stalemate')
        self.menu.add.button('Exit', self._on_exit_press,
                             onselect=self._on_select)

    def draw(self, window: pygame.Surface, events: List[pygame.event.Event]) -> None:
        """Render the game over menu overlay.

        :param window: The pygame surface to draw on
        :param events: Current frame's pygame events for menu interaction
        """
        _draw_overlay(window)
        self.menu.update(events)
        self.menu.draw(window)
