"""GUI abstraction that wraps all rendering and sound into a single API."""
from math import floor
from typing import List, Tuple

import pygame

from pychess import constants
from pychess.gui.gui_utils import draw_board as _draw_board, draw_solid_rect, draw_solid_circle
from pychess.gui.sprites import Sprites
from pychess.gui.sounds import Sounds
from pychess.state.game_state import GameState


class GUIManager:
    """Facade for all rendering and audio operations."""

    def __init__(self, window: pygame.Surface, sounds: Sounds) -> None:
        self._window: pygame.Surface = window
        self._sprites: Sprites = Sprites(window)
        self.sounds: Sounds = sounds

    # ==== Board Rendering ==== #

    def draw_board(self) -> None:
        """Draw the chess board background (alternating light/dark squares)."""
        _draw_board(self._window)

    def draw_piece(self, piece_code: str, x: int, y: int) -> None:
        """Draw a piece at board square (x, y).

        :param piece_code: The piece code (e.g. 'pl')
        :param x: Row index
        :param y: Column index
        """
        source = self._sprites.get_sprite_from_code(
            piece_code, constants.SQ_HEIGHT, constants.SQ_HEIGHT)
        dest = (constants.SQ_HEIGHT * y, constants.SQ_HEIGHT * x)
        if source and dest:
            self._window.blit(source, dest)

    def draw_dragged_piece(
        self, piece_code: str, cursor_pos: Tuple[int, int], start_sq: Tuple[int, int], cursor_sq: Tuple[int, int],
    ) -> None:
        """Draw the piece being dragged, scaled up if moved away from its start square.

        :param piece_code: The piece code being dragged
        :param cursor_pos: Current (x, y) pixel position of the cursor
        :param start_sq: The (row, col) square the piece was picked up from
        :param cursor_sq: The (row, col) square the cursor is currently over
        """
        if start_sq != cursor_sq:
            scale = floor(constants.SQ_HEIGHT * 1.1)
            x, y = cursor_pos
            surface = self._sprites.get_sprite_from_code(
                piece_code, scale, scale)
            self._window.blit(surface, (y - scale / 2, x - scale / 2))
        else:
            scale = constants.SQ_HEIGHT
            x, y = start_sq[0] * scale, start_sq[1] * scale
            surface = self._sprites.get_sprite_from_code(
                piece_code, scale, scale)
            self._window.blit(surface, (y, x))

    # ==== Overlays ==== #

    def draw_square_highlight(self, x: int, y: int) -> None:
        """Draw a highlight overlay on a board square.

        :param x: Row index
        :param y: Column index
        """
        draw_solid_rect(
            self._window, constants.SQ_HEIGHT, constants.SQ_HEIGHT,
            constants.SQ_HEIGHT * x, constants.SQ_HEIGHT * y,
            constants.SQ_HIGHLIGHT_COLOR, constants.SQ_HIGHLIGHT_ALPHA,
        )

    def draw_move_hint(self, x: int, y: int) -> None:
        """Draw a valid-move hint dot on a board square.

        :param x: Row index
        :param y: Column index
        """
        draw_solid_circle(
            self._window, constants.SQ_HEIGHT, constants.SQ_HEIGHT,
            constants.SQ_HEIGHT / 7,
            constants.SQ_HEIGHT * x, constants.SQ_HEIGHT * y,
            constants.SQ_HINT_COLOR, constants.SQ_HINT_ALPHA,
        )

    # ==== Composite Drawing ==== #

    def draw_pieces(self, game_state: GameState, board_width: int, board_height: int) -> None:
        """Draw all pieces currently on the board.

        :param game_state: GameState representing the board
        :param board_width: Number of columns
        :param board_height: Number of rows
        """
        for x in range(board_width):
            for y in range(board_height):
                code = game_state.get_piece(x, y)
                if code:
                    self.draw_piece(code, x, y)

    def draw_overlays(
        self,
        drag_piece: str,
        start_sq: Tuple[int, int],
        cursor_sq: Tuple[int, int],
        cursor_pos: Tuple[int, int],
        valid_moves: List[Tuple[int, int]],
    ) -> None:
        """Draw selection highlights, move hints, and the dragged piece sprite.

        :param drag_piece: The piece code being dragged, or '' if none
        :param start_sq: The (row, col) the piece was picked up from
        :param cursor_sq: The (row, col) the cursor is currently over
        :param cursor_pos: Current (x, y) pixel position of the cursor
        :param valid_moves: List of (row, col) tuples the piece can move to
        """
        if drag_piece:
            self.draw_square_highlight(*start_sq)
            self.draw_square_highlight(*cursor_sq)

            for sqx, sqy in valid_moves:
                self.draw_move_hint(sqx, sqy)

            self.draw_dragged_piece(
                drag_piece, cursor_pos, start_sq, cursor_sq)
