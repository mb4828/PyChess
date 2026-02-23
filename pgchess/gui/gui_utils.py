"""Low-level GUI utility functions for drawing and resource path resolution."""
import os
import sys
from typing import Tuple

import pygame

from pgchess import constants


def get_resource_path(file_path: str) -> str:
    """Resolve the correct path for bundled assets.

    PyInstaller stores assets in a temp directory (sys._MEIPASS) when running
    as a frozen executable; this falls back to the raw path in development.

    :param file_path: Relative asset path (e.g. 'assets/images/pgchess.png')
    :return: Resolved absolute or relative path
    """
    try:
        return os.path.join(sys._MEIPASS, file_path)  # type: ignore[attr-defined]  # pylint: disable=protected-access
    except AttributeError:
        return file_path


def draw_board(window: pygame.Surface) -> None:
    """Draw the alternating light/dark chess board squares.

    :param window: The pygame surface to draw on
    """
    for x in range(constants.BOARD_WIDTH):
        for y in range(constants.BOARD_HEIGHT):
            color = constants.SQ_LIGHT_COLOR if (x + y) % 2 == 0 else constants.SQ_DARK_COLOR
            rect = (constants.SQ_HEIGHT * y, constants.SQ_HEIGHT * x, constants.SQ_HEIGHT, constants.SQ_HEIGHT)
            pygame.draw.rect(window, color, rect)


def draw_solid_rect(
    window: pygame.Surface,
    width: int,
    height: int,
    x_position: int,
    y_position: int,
    color: Tuple[int, int, int],
    alpha: int = 255,
) -> None:
    """Draw a filled rectangle with optional transparency.

    :param window: The pygame surface to draw on
    :param width: Rectangle width in pixels
    :param height: Rectangle height in pixels
    :param x_position: X offset on the window
    :param y_position: Y offset on the window
    :param color: RGB fill color
    :param alpha: Transparency (0 = fully transparent, 255 = opaque)
    """
    surface = pygame.Surface((width, height))
    surface.set_alpha(alpha)
    surface.fill(color)
    window.blit(surface, (y_position, x_position))


def draw_solid_circle(
    window: pygame.Surface,
    width: int,
    height: int,
    radius: float,
    x_position: int,
    y_position: int,
    color: Tuple[int, int, int],
    alpha: int = 255,
) -> None:
    """Draw a filled circle with optional transparency.

    :param window: The pygame surface to draw on
    :param width: Bounding surface width in pixels
    :param height: Bounding surface height in pixels
    :param radius: Circle radius in pixels
    :param x_position: X offset on the window
    :param y_position: Y offset on the window
    :param color: RGB fill color
    :param alpha: Transparency (0 = fully transparent, 255 = opaque)
    """
    surface = pygame.Surface((width, height))
    surface.set_alpha(alpha)
    center = (width / 2, height / 2)
    pygame.draw.circle(surface, color, center, radius)
    window.blit(surface, (y_position, x_position))
