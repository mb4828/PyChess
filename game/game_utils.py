"""
Game utility functions
"""
import os
import sys

import pygame

import constants


def get_resource_path(file_path):
    """
    Takes a raw file path and returns the correct path to find it since it differs when we're running as exe
    """
    try:
        return os.path.join(sys._MEIPASS, file_path)
    except Exception:
        return file_path


def draw_board(window):
    """
    Draws the board
    """
    for x in range(0, constants.BOARD_WIDTH):
        for y in range(0, constants.BOARD_HEIGHT):
            if (x % 2 == 0 and y % 2 == 0) or (x % 2 != 0 and y % 2 != 0):
                color = constants.SQ_LIGHT_COLOR
            else:
                color = constants.SQ_DARK_COLOR
            rect = (constants.SQ_HEIGHT * y, constants.SQ_HEIGHT * x, constants.SQ_HEIGHT, constants.SQ_HEIGHT)
            pygame.draw.rect(window, color, rect)


def draw_solid_rect(window, width, height, x_position, y_position, color, alpha=255):
    """
    Draws a rectangle with solid fill color and optional transparency
    """
    surface = pygame.Surface((width, height))
    surface.set_alpha(alpha)
    surface.fill(color)
    window.blit(surface, (y_position, x_position))


def draw_solid_circle(window, width, height, radius, x_position, y_position, color, alpha=255):
    """
    Draws a circle with solid fill color and optional transparency
    """
    surface = pygame.Surface((width, height))
    surface.set_alpha(alpha)
    center = (width / 2, height / 2)
    pygame.draw.circle(surface, color, center, radius)
    window.blit(surface, (y_position, x_position))