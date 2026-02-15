"""
GUI abstraction that wraps all rendering and sound into a single API.
"""

from math import floor

import pychess.constants as constants
from .gui_utils import draw_board as _draw_board, draw_solid_rect, draw_solid_circle
from .sprites import Sprites
from . import sounds


class GUI:
    def __init__(self, window):
        self.window = window
        self.sprites = Sprites(window)

    # Board rendering

    def draw_board(self):
        _draw_board(self.window)

    def draw_piece(self, piece_code, x, y):
        """Draws a piece at board square (x, y)."""
        source = self.sprites.get_sprite_from_code(
            piece_code, constants.SQ_HEIGHT, constants.SQ_HEIGHT)
        dest = (constants.SQ_HEIGHT * y, constants.SQ_HEIGHT * x)
        if source and dest:
            self.window.blit(source, dest)

    def draw_dragged_piece(self, piece_code, cursor_pos, start_sq, cursor_sq):
        """Draws the piece being dragged, scaled up if moved from start square."""
        if start_sq != cursor_sq:
            scale = floor(constants.SQ_HEIGHT * 1.1)
            x, y = cursor_pos
            surface = self.sprites.get_sprite_from_code(
                piece_code, scale, scale)
            self.window.blit(surface, (y - scale / 2, x - scale / 2))
        else:
            scale = constants.SQ_HEIGHT
            x, y = start_sq[0] * scale, start_sq[1] * scale
            surface = self.sprites.get_sprite_from_code(
                piece_code, scale, scale)
            self.window.blit(surface, (y, x))

    # Overlays

    def draw_square_highlight(self, x, y):
        """Highlights a square on the board."""
        draw_solid_rect(self.window, constants.SQ_HEIGHT, constants.SQ_HEIGHT,
                        constants.SQ_HEIGHT * x, constants.SQ_HEIGHT * y,
                        constants.SQ_HIGHLIGHT_COLOR, constants.SQ_HIGHLIGHT_ALPHA)

    def draw_move_hint(self, x, y):
        """Draws a valid move hint dot on a square."""
        draw_solid_circle(self.window, constants.SQ_HEIGHT, constants.SQ_HEIGHT,
                          constants.SQ_HEIGHT / 7,
                          constants.SQ_HEIGHT * x, constants.SQ_HEIGHT * y,
                          constants.SQ_HINT_COLOR, constants.SQ_HINT_ALPHA)

    # Composite drawing

    def draw_pieces(self, board, board_width, board_height):
        """Draws all pieces on the board."""
        for x in range(0, board_width):
            for y in range(0, board_height):
                code = board[x][y]
                if code:
                    self.draw_piece(code, x, y)

    def draw_overlays(self, drag_piece, start_sq, cursor_sq, cursor_pos, valid_moves):
        """Draws overlays such as highlighted tiles, possible moves, and dragged piece."""
        if drag_piece:
            self.draw_square_highlight(*start_sq)
            self.draw_square_highlight(*cursor_sq)

            for sqx, sqy in valid_moves:
                self.draw_move_hint(sqx, sqy)

            self.draw_dragged_piece(drag_piece, cursor_pos, start_sq, cursor_sq)

    # Sounds

    def play_game_start(self):
        sounds.play_game_start()

    def play_game_over(self):
        sounds.play_game_over()

    def play_error(self):
        sounds.play_error()

    def play_move(self, is_capture, is_dark=False):
        if is_capture:
            sounds.play_piece_capture()
        else:
            sounds.play_piece_move(is_dark)

    def play_check(self):
        sounds.play_piece_check()
