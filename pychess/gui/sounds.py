"""Sound effect playback functions."""
import pygame

from pychess import constants
from .gui_utils import get_resource_path


class Sounds:
    """Class for managing sound effects."""

    def __init__(self) -> None:
        """Initialize the Sounds instance."""
        pygame.mixer.init()

    def __del__(self) -> None:
        """Clean up the mixer on deletion."""
        pygame.mixer.quit()

    def _play(self, path: str, volume: float = 1.0) -> None:
        """Load and play a sound asset.

        :param path: Relative path to the sound file
        :param volume: Volume level (0.0 to 1.0)
        """
        sound = pygame.mixer.Sound(get_resource_path(path))
        sound.set_volume(volume)
        sound.play()

    def play_game_start(self) -> None:
        """Play the game-start sound."""
        self._play(constants.PATH_GAME_START)

    def play_game_over(self) -> None:
        """Play the game-over sound."""
        self._play(constants.PATH_GAME_OVER)

    def play_error(self) -> None:
        """Play the invalid-move error sound."""
        self._play(constants.PATH_ERROR)

    def play_piece_capture(self) -> None:
        """Play the piece-capture sound."""
        self._play(constants.PATH_PIECE_CAPTURE)

    def play_piece_check(self) -> None:
        """Play the check sound."""
        self._play(constants.PATH_PIECE_CHECK)

    def play_piece_move(self, is_capture: bool = False, is_dark: bool = False) -> None:
        """Play the piece-move sound.

        :param is_capture: If True, play the capture sound instead of the regular move sound
        :param is_dark: If True, use the alternate sound for dark-player moves
        """
        if is_capture:
            self.play_piece_capture()
            return
        path = constants.PATH_PIECE_MOVE_2 if is_dark else constants.PATH_PIECE_MOVE
        self._play(path)

    def play_menu_click(self) -> None:
        """Play the menu-click sound."""
        self._play(constants.PATH_MENU_CLICK, volume=0.25)

    def play_menu_confirm(self) -> None:
        """Play the menu-selection sound."""
        self._play(constants.PATH_MENU_CONFIRM)
