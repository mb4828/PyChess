"""Tests for en passant logic"""
from pgchess.state.game_context import GameContext
from pgchess.state.game_state import GameState
from pgchess.state.move_validator import get_valid_moves
from pgchess.state.move_executor import execute_move


def empty_board() -> GameState:
    """Return a fresh empty GameState for test setup."""
    return GameState.empty()


def default_context() -> GameContext:
    """Return a fresh default GameContext for test setup."""
    return GameContext()


class TestEnPassantValidation:
    """Tests for en passant move availability based on context target."""

    def test_light_pawn_en_passant_left(self):
        """Light pawn should be able to capture en passant to the left when target is set."""
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        board.set_piece(3, 3, 'pd')  # dark pawn just moved 2 squares to land here
        ctx = default_context()
        ctx.set_en_passant_target((2, 3))  # the square the dark pawn skipped
        moves = get_valid_moves(board, ctx, 'pl', 3, 4)
        assert (2, 3) in moves

    def test_light_pawn_en_passant_right(self):
        """Light pawn should be able to capture en passant to the right when target is set."""
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        board.set_piece(3, 5, 'pd')
        ctx = default_context()
        ctx.set_en_passant_target((2, 5))
        moves = get_valid_moves(board, ctx, 'pl', 3, 4)
        assert (2, 5) in moves

    def test_dark_pawn_en_passant(self):
        """Dark pawn should be able to capture en passant when target is set."""
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        board.set_piece(4, 4, 'pl')  # light pawn just moved 2 squares
        ctx = default_context()
        ctx.set_en_passant_target((5, 4))
        moves = get_valid_moves(board, ctx, 'pd', 4, 3)
        assert (5, 4) in moves

    def test_no_en_passant_without_target(self):
        """En passant diagonal should not appear in moves when no target is set."""
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        board.set_piece(3, 3, 'pd')
        ctx = default_context()
        moves = get_valid_moves(board, ctx, 'pl', 3, 4)
        assert (2, 3) not in moves

    def test_no_en_passant_wrong_row_light(self):
        """En passant should not be available when the pawn is not on the correct rank."""
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        ctx = default_context()
        ctx.set_en_passant_target((3, 3))
        moves = get_valid_moves(board, ctx, 'pl', 4, 4)
        assert (3, 3) not in moves

    def test_no_en_passant_too_far(self):
        """En passant target that is not adjacent to the pawn should not appear in moves."""
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(0, 4, 'kd')
        ctx = default_context()
        ctx.set_en_passant_target((2, 6))  # too far away
        moves = get_valid_moves(board, ctx, 'pl', 3, 4)
        assert (2, 6) not in moves


class TestEnPassantExecution:
    """Tests that execute_move correctly removes the captured pawn during en passant."""

    def test_en_passant_removes_captured_pawn_light(self):
        """Light pawn en passant should move to the target and remove the dark pawn beside it."""
        board = empty_board()
        board.set_piece(3, 4, 'pl')
        board.set_piece(3, 3, 'pd')  # the pawn to be captured
        execute_move(board, 'pl', 3, 4, 2, 3, is_en_passant=True)
        assert board.get_piece(2, 3) == 'pl'  # pawn moved to en passant square
        assert board.get_piece(3, 4) == ''    # origin cleared
        assert board.get_piece(3, 3) == ''    # captured pawn removed

    def test_en_passant_removes_captured_pawn_dark(self):
        """Dark pawn en passant should move to the target and remove the light pawn beside it."""
        board = empty_board()
        board.set_piece(4, 3, 'pd')
        board.set_piece(4, 4, 'pl')  # the pawn to be captured
        execute_move(board, 'pd', 4, 3, 5, 4, is_en_passant=True)
        assert board.get_piece(5, 4) == 'pd'  # pawn moved to en passant square
        assert board.get_piece(4, 3) == ''    # origin cleared
        assert board.get_piece(4, 4) == ''    # captured pawn removed

    def test_normal_capture_not_en_passant(self):
        """A normal diagonal capture (is_en_passant=False) should not remove any extra piece."""
        board = empty_board()
        board.set_piece(3, 4, 'pl')
        board.set_piece(2, 3, 'pd')  # normal diagonal capture target
        execute_move(board, 'pl', 3, 4, 2, 3, is_en_passant=False)
        assert board.get_piece(2, 3) == 'pl'
        assert board.get_piece(3, 4) == ''
