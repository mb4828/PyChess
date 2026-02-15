"""
Base Game class containing shared game logic for all game modes.
"""

from math import floor

import pygame
from pygame.event import Event

import pychess.constants as constants
from pychess.gui.gui import GUI
from pychess.engine.engine import GameEngine


class Game:
    drag_piece = ''
    drag_piece_start_sq = (0, 0)
    drag_piece_cursor_sq = (0, 0)
    drag_piece_cursor_pos = (0, 0)
    drag_piece_valid_moves = []
    pending_promotion = None

    def __init__(self, window):
        self.gui = GUI(window)
        self.engine = GameEngine()
        self.gui.play_game_start()

    def drag_start(self, x, y):
        """
        Triggered when user picks up a piece to make a move
        :param x: Mouse x coordinate
        :param y: Mouse y coordinate
        """
        self.drag_piece = ''
        sqx, sqy = floor(x / constants.SQ_HEIGHT), floor(y /
                                                         constants.SQ_HEIGHT)
        piece = self.engine.get_piece(sqx, sqy)
        if piece and self.engine.is_turn(piece):
            self.engine.state.clear_square(sqx, sqy)
            self.drag_piece = piece
            self.drag_piece_start_sq = (sqx, sqy)
            self.drag_piece_cursor_sq = (sqx, sqy)
            self.drag_piece_valid_moves = self.engine.get_valid_moves(
                self.drag_piece, sqx, sqy)

    def drag_continue(self, x, y):
        """
        Triggered when user continues dragging piece
        :param x: Mouse x coordinate
        :param y: Mouse y coordinate
        """
        if self.drag_piece:
            sqx, sqy = floor(
                x / constants.SQ_HEIGHT), floor(y / constants.SQ_HEIGHT)
            self.drag_piece_cursor_sq = (sqx, sqy)
            self.drag_piece_cursor_pos = (x, y)

    def drag_stop(self):
        """
        Triggers when user drops a piece (or nothing if a piece was not held). Executes the move if valid
        """
        if self.drag_piece:
            if self.drag_piece_cursor_sq in self.drag_piece_valid_moves:
                # valid move - execute move via engine
                sqx, sqy = self.drag_piece_cursor_sq
                start_sqx, start_sqy = self.drag_piece_start_sq

                result = self.engine.execute_move(
                    self.drag_piece, start_sqx, start_sqy, sqx, sqy)

                # check for pawn promotion
                if result['is_promotion']:
                    self.pending_promotion = result['promotion_square']
                    self.drag_piece = ''
                    pygame.event.post(Event(constants.EVENT_PROMOTION))
                    return

                # move complete
                self._on_move_complete(result['is_capture'])

            elif self.drag_piece_cursor_sq != self.drag_piece_start_sq:
                # invalid move - return piece to previous position
                sqx, sqy = self.drag_piece_start_sq
                self.engine.state.set_piece(sqx, sqy, self.drag_piece)
                self.gui.play_error()
                self.drag_piece = ''

            else:
                # piece hasn't moved - return piece to previous position but don't clear drag_piece to keep highlights
                sqx, sqy = self.drag_piece_start_sq
                self.engine.state.set_piece(sqx, sqy, self.drag_piece)
                return
            self.drag_piece = ''

    def complete_promotion(self, piece_type):
        """
        Called when player selects a piece for pawn promotion.
        :param piece_type: The piece type character (e.g. 'q', 'r', 'b', 'n')
        """
        if self.pending_promotion:
            px, py = self.pending_promotion
            self.engine.promote_pawn(px, py, piece_type)
            self.pending_promotion = None
            self._on_move_complete(False)

    def _on_move_complete(self, is_capture):
        """
        Hook called after a valid move is executed. Subclasses can override
        to add mode-specific behavior (e.g. trigger AI move).
        Default: switch turn and run post-move checks.
        """
        self.engine.switch_turn()
        self._post_move_checks(is_capture)

    def _post_move_checks(self, is_capture):
        """
        Runs check/checkmate/stalemate detection and plays sounds after a move.
        """
        color = self.engine.current_color()
        if self.engine.is_in_checkmate(color):
            event_type = constants.EVENT_BLACK_WINS if color == 'l' else constants.EVENT_WHITE_WINS
            pygame.event.post(Event(event_type))
            self.gui.play_game_over()
        elif self.engine.is_in_stalemate(color):
            pygame.event.post(Event(constants.EVENT_DRAW))
            self.gui.play_game_over()
        elif self.engine.is_in_check(color):
            self.gui.play_check()
        else:
            self.gui.play_move(is_capture, 'd' in self.drag_piece)

    def draw(self):
        """
        Draws the current state of the game
        """
        self.gui.draw_board()
        self.gui.draw_pieces(self.engine.state.board,
                             constants.BOARD_WIDTH, constants.BOARD_HEIGHT)
        self.gui.draw_overlays(self.drag_piece, self.drag_piece_start_sq,
                               self.drag_piece_cursor_sq,
                               self.drag_piece_cursor_pos,
                               self.drag_piece_valid_moves)
