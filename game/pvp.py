"""
Player vs. player (PVP) game
"""

from math import floor

import pygame
from pygame.event import Event

import constants
from game import sounds
from game.game_utils import draw_board, draw_solid_rect, draw_solid_circle
from game.sprites import Sprites
from logic import move_executor, move_validator, move_utils


class PVPGame:
    is_light_turn = True  # whether or not it's light color's turn
    drag_piece = ''  # dragged piece code
    drag_piece_start_sq = (0, 0)  # start square of dragged piece
    drag_piece_cursor_sq = (0, 0)  # cursor square when dragging
    drag_piece_cursor_pos = (0, 0)  # cursor position when dragging
    drag_piece_valid_moves = []  # valid moves for the dragged piece

    def __init__(self, window):
        self.sprites = Sprites(window)
        self.game_window = window
        self.game_state = [
            ['rd', 'nd', 'bd', 'qd', 'kd', 'bd', 'nd', 'rd'],
            ['pd', 'pd', 'pd', 'pd', 'pd', 'pd', 'pd', 'pd'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['pl', 'pl', 'pl', 'pl', 'pl', 'pl', 'pl', 'pl'],
            ['rl', 'nl', 'bl', 'ql', 'kl', 'bl', 'nl', 'rl']
        ]
        sounds.play_game_start()

    def drag_start(self, x, y):
        """
        Triggered when user picks up a piece to make a move
        :param x: Mouse x coordinate
        :param y: Mouse y coordinate
        """
        self.drag_piece = ''
        sqx, sqy = floor(x / constants.SQ_HEIGHT), floor(y / constants.SQ_HEIGHT)
        piece = self.game_state[sqx][sqy]
        if piece and self.__is_turn(piece):
            # remove the piece from the game state, store start square and cursor position, and calculate valid moves
            self.game_state[sqx][sqy] = ''
            self.drag_piece = piece
            self.drag_piece_start_sq = (sqx, sqy)
            self.drag_piece_cursor_sq = (sqx, sqy)
            self.drag_piece_valid_moves = move_validator.get_valid_moves(self.game_state, self.drag_piece, sqx, sqy)

    def drag_continue(self, x, y):
        """
        Triggered when user continues dragging piece
        :param x: Mouse x coordinate
        :param y: Mouse y coordinate
        """
        if self.drag_piece:
            # store cursor position
            sqx, sqy = floor(x / constants.SQ_HEIGHT), floor(y / constants.SQ_HEIGHT)
            self.drag_piece_cursor_sq = (sqx, sqy)
            self.drag_piece_cursor_pos = (x, y)

    def drag_stop(self):
        """
        Triggers when user drops a piece (or nothing if a piece was not held). Executes the move if valid
        """
        if self.drag_piece:
            if self.drag_piece_cursor_sq in self.drag_piece_valid_moves:
                # valid move - execute move
                sqx, sqy = self.drag_piece_cursor_sq
                start_sqx, start_sqy = self.drag_piece_start_sq
                is_capture = move_utils.is_piece_at(self.game_state, sqx, sqy)
                self.game_state = move_executor.execute_move(self.game_state, self.drag_piece, start_sqx, start_sqy, sqx, sqy)

                # switch turn to opposing player
                self.is_light_turn = not self.is_light_turn

                if move_validator.is_in_checkmate(self.game_state, 'l' if self.is_light_turn else 'd'):
                    # in checkmate
                    event_type = constants.EVENT_BLACK_WINS if self.is_light_turn else constants.EVENT_WHITE_WINS
                    pygame.event.post(Event(event_type))
                    sounds.play_game_over()
                elif move_validator.is_in_check(self.game_state, 'l' if self.is_light_turn else 'd'):
                    # in check
                    sounds.play_piece_check()
                else:
                    # play fun sounds
                    if is_capture:
                        sounds.play_piece_capture()
                    else:
                        sounds.play_piece_move('d' in self.drag_piece)

            elif self.drag_piece_cursor_sq != self.drag_piece_start_sq:
                # invalid move - return piece to previous position
                sqx, sqy = self.drag_piece_start_sq
                self.game_state[sqx][sqy] = self.drag_piece
                sounds.play_error()
                self.drag_piece = ''

            else:
                # piece hasn't moved - return piece to previous position but don't clear drag_piece to keep highlights
                sqx, sqy = self.drag_piece_start_sq
                self.game_state[sqx][sqy] = self.drag_piece
                return
            self.drag_piece = ''

    def draw(self):
        """
        Draws the current state of the game
        """
        draw_board(self.game_window)
        self.__draw_pieces()
        self.__draw_overlays()

    def __draw_pieces(self):
        """
        Draws the pieces on the board
        """
        for x in range(0, constants.BOARD_WIDTH):
            for y in range(0, constants.BOARD_HEIGHT):
                code = self.game_state[x][y]
                source = self.sprites.get_sprite_from_code(code, constants.SQ_HEIGHT, constants.SQ_HEIGHT)
                dest = (constants.SQ_HEIGHT * y, constants.SQ_HEIGHT * x)
                if source and dest:
                    self.game_window.blit(source, dest)

    def __draw_overlays(self):
        """
        Draws overlays such as highlighted tiles on the board, possible moves, etc.
        """
        if self.drag_piece:
            # highlight drag start square
            sqx, sqy = self.drag_piece_start_sq
            draw_solid_rect(self.game_window, constants.SQ_HEIGHT, constants.SQ_HEIGHT,
                            constants.SQ_HEIGHT * sqx, constants.SQ_HEIGHT * sqy,
                            constants.SQ_HIGHLIGHT_COLOR, constants.SQ_HIGHLIGHT_ALPHA)

            # highlight current cursor square
            sqx, sqy = self.drag_piece_cursor_sq
            draw_solid_rect(self.game_window, constants.SQ_HEIGHT, constants.SQ_HEIGHT,
                            constants.SQ_HEIGHT * sqx, constants.SQ_HEIGHT * sqy,
                            constants.SQ_HIGHLIGHT_COLOR, constants.SQ_HIGHLIGHT_ALPHA)

            # show valid move hints
            for sqx, sqy in self.drag_piece_valid_moves:
                draw_solid_circle(self.game_window, constants.SQ_HEIGHT, constants.SQ_HEIGHT, constants.SQ_HEIGHT / 7,
                                  constants.SQ_HEIGHT * sqx, constants.SQ_HEIGHT * sqy,
                                  constants.SQ_HINT_COLOR, constants.SQ_HINT_ALPHA)

            # show piece being dragged
            if self.drag_piece_start_sq != self.drag_piece_cursor_sq:
                scale = floor(constants.SQ_HEIGHT * 1.1)
                x, y = self.drag_piece_cursor_pos
                surface = self.sprites.get_sprite_from_code(self.drag_piece, scale, scale)
                self.game_window.blit(surface, (y - scale/2, x - scale/2))
            else:
                scale = constants.SQ_HEIGHT
                x, y = self.drag_piece_start_sq[0] * scale, self.drag_piece_start_sq[1] * scale
                surface = self.sprites.get_sprite_from_code(self.drag_piece, scale, scale)
                self.game_window.blit(surface, (y, x))

    def __is_turn(self, piece):
        """
        Accepts a piece and returns a boolean indicating whether or not this it's this color's turn to move
        :param piece:
        :return: boolean
        """
        return (self.is_light_turn and 'l' in piece) or (not self.is_light_turn and 'd' in piece)
