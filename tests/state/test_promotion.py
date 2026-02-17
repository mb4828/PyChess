"""Tests for pawn promotion detection"""
from pychess.state.game_context import GameContext
from pychess.state.game_state import GameState
from pychess.state.move_validator import get_valid_moves
from pychess.state.move_executor import execute_move


def empty_board() -> GameState:
    return GameState.empty()


class TestPromotionDetection:
    def test_light_pawn_can_reach_promotion_rank(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        board.set_piece(1, 3, 'pl')  # one square from promotion
        board.clear_square(1, 3)
        moves = get_valid_moves(board, GameContext(), 'pl',1, 3)
        assert (0, 3) in moves  # can move to back rank

    def test_dark_pawn_can_reach_promotion_rank(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        board.set_piece(6, 3, 'pd')  # one square from promotion
        board.clear_square(6, 3)
        moves = get_valid_moves(board, GameContext(), 'pd',6, 3)
        assert (7, 3) in moves  # can move to back rank

    def test_promotion_square_detection_light(self):
        """Verify that a pawn at row 1 moving to row 0 triggers promotion logic"""
        board = empty_board()
        board.set_piece(1, 3, 'pl')
        execute_move(board, 'pl', 1, 3, 0, 3)
        # After execute_move, the pawn is at (0, 3) - pvp.py would detect this and trigger promotion
        assert board.get_piece(0, 3) == 'pl'
        assert board.get_piece(1, 3) == ''

    def test_promotion_square_detection_dark(self):
        """Verify that a pawn at row 6 moving to row 7 triggers promotion logic"""
        board = empty_board()
        board.set_piece(6, 3, 'pd')
        execute_move(board, 'pd', 6, 3, 7, 3)
        assert board.get_piece(7, 3) == 'pd'
        assert board.get_piece(6, 3) == ''

    def test_promotion_with_capture(self):
        """Pawn can promote by capturing a piece on the back rank"""
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        board.set_piece(1, 3, 'pl')
        board.set_piece(0, 2, 'nd')  # piece to capture
        board.clear_square(1, 3)
        moves = get_valid_moves(board, GameContext(), 'pl',1, 3)
        assert (0, 2) in moves  # can capture and promote
