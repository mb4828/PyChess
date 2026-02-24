"""Shared fixtures for game mode tests."""
import os

import pygame
import pytest


@pytest.fixture(autouse=True, scope='session')
def init_pygame():
    """Initialize pygame with dummy drivers for headless test execution."""
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    pygame.init()
    pygame.display.set_mode((600, 600))
    yield
    pygame.quit()
