"""
Game menus
"""
import pygame_menu
from pygame_menu.themes import Theme

import constants
from game.game_utils import draw_board, draw_solid_rect, get_resource_path

MENU_THEME = Theme(background_color=(255, 255, 255, 255),
                   menubar_close_button=False,
                   selection_color=(110, 148, 205, 255),
                   title_background_color=(110, 148, 205, 255),
                   title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
                   title_font_size=1,
                   title_shadow=False,
                   widget_font=pygame_menu.font.FONT_OPEN_SANS,
                   widget_font_color=(0, 0, 0, 255))


class StartMenu:
    def __init__(self, on_start_press, on_quit_press):
        self.menu = pygame_menu.Menu(250, 300, '', theme=MENU_THEME, mouse_motion_selection=True)
        self.menu.add_image(get_resource_path(constants.PATH_LOGO), scale=(.6, .6), scale_smooth=True)
        self.menu.add_button('Play', on_start_press)
        self.menu.add_button('Quit', on_quit_press)

    def draw(self, window, events):
        draw_board(window)
        draw_solid_rect(window, constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, 0, 0, (0, 0, 0), 85)
        self.menu.update(events)
        self.menu.draw(window)


class PauseMenu:
    def __init__(self, on_resume_press, on_resign_press):
        self.menu = pygame_menu.Menu(250, 300, '', theme=MENU_THEME, mouse_motion_selection=True)
        self.menu.add_button('Resume', on_resume_press)
        self.menu.add_button('Resign', on_resign_press)

    def draw(self, window, events):
        draw_solid_rect(window, constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, 0, 0, (0, 0, 0), 85)
        self.menu.update(events)
        self.menu.draw(window)


class GameOverMenu:
    def __init__(self, on_exit_press):
        self.menu = pygame_menu.Menu(250, 300, '', theme=MENU_THEME, mouse_motion_selection=True)
        self.on_exit_press = on_exit_press

    def set_winner(self, white_wins):
        self.menu.clear()
        self.menu.add_label('White wins' if white_wins else 'Black wins')
        self.menu.add_button('Exit', self.on_exit_press)

    def draw(self, window, events):
        draw_solid_rect(window, constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, 0, 0, (0, 0, 0), 85)
        self.menu.update(events)
        self.menu.draw(window)
