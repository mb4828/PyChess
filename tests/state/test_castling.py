"""Tests for castling logic"""
from pgchess.state.game_context import GameContext
from pgchess.state.game_state import GameState
from pgchess.state.move_validator import get_valid_moves
from pgchess.state.move_executor import execute_move


def empty_board() -> GameState:
    return GameState.empty()


def default_context() -> GameContext:
    return GameContext()


class TestCastlingValidation:
    def test_kingside_castle_light(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 7, 'rl')
        board.clear_square(7, 4)  # remove king (simulating drag_start)
        moves = get_valid_moves(board, default_context(), 'kl', 7, 4)
        assert (7, 6) in moves

    def test_queenside_castle_light(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 0, 'rl')
        board.clear_square(7, 4)
        moves = get_valid_moves(board, default_context(), 'kl', 7, 4)
        assert (7, 2) in moves

    def test_kingside_castle_dark(self):
        board = empty_board()
        board.set_piece(0, 4, 'kd')
        board.set_piece(0, 7, 'rd')
        board.clear_square(0, 4)
        moves = get_valid_moves(board, default_context(), 'kd', 0, 4)
        assert (0, 6) in moves

    def test_queenside_castle_dark(self):
        board = empty_board()
        board.set_piece(0, 4, 'kd')
        board.set_piece(0, 0, 'rd')
        board.clear_square(0, 4)
        moves = get_valid_moves(board, default_context(), 'kd', 0, 4)
        assert (0, 2) in moves

    def test_cannot_castle_after_king_moved(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 7, 'rl')
        board.clear_square(7, 4)
        ctx = default_context()
        ctx.mark_king_moved('l')
        moves = get_valid_moves(board, ctx, 'kl', 7, 4)
        assert (7, 6) not in moves

    def test_cannot_castle_after_rook_moved(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 7, 'rl')
        board.clear_square(7, 4)
        ctx = default_context()
        ctx.mark_rook_moved('l', 7)
        moves = get_valid_moves(board, ctx, 'kl', 7, 4)
        assert (7, 6) not in moves

    def test_cannot_castle_with_piece_in_way_kingside(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 7, 'rl')
        board.set_piece(7, 5, 'bl')  # bishop blocking
        board.clear_square(7, 4)
        moves = get_valid_moves(board, default_context(), 'kl', 7, 4)
        assert (7, 6) not in moves

    def test_cannot_castle_with_piece_in_way_queenside(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 0, 'rl')
        board.set_piece(7, 1, 'nl')  # knight blocking
        board.clear_square(7, 4)
        moves = get_valid_moves(board, default_context(), 'kl', 7, 4)
        assert (7, 2) not in moves

    def test_cannot_castle_while_in_check(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 7, 'rl')
        board.set_piece(0, 4, 'rd')  # rook giving check
        board.clear_square(7, 4)
        moves = get_valid_moves(board, default_context(), 'kl', 7, 4)
        assert (7, 6) not in moves

    def test_cannot_castle_through_check(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 7, 'rl')
        # rook attacking f1 (the square king passes through)
        board.set_piece(0, 5, 'rd')
        board.clear_square(7, 4)
        moves = get_valid_moves(board, default_context(), 'kl', 7, 4)
        assert (7, 6) not in moves

    def test_cannot_castle_into_check(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 7, 'rl')
        board.set_piece(0, 6, 'rd')  # rook attacking g1 (destination)
        board.clear_square(7, 4)
        moves = get_valid_moves(board, default_context(), 'kl', 7, 4)
        assert (7, 6) not in moves


class TestCastlingExecution:
    def test_kingside_castle_moves_rook(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 7, 'rl')
        execute_move(board, 'kl', 7, 4, 7, 6)
        assert board.get_piece(7, 6) == 'kl'
        assert board.get_piece(7, 5) == 'rl'
        assert board.get_piece(7, 7) == ''
        assert board.get_piece(7, 4) == ''

    def test_queenside_castle_moves_rook(self):
        board = empty_board()
        board.set_piece(7, 4, 'kl')
        board.set_piece(7, 0, 'rl')
        execute_move(board, 'kl', 7, 4, 7, 2)
        assert board.get_piece(7, 2) == 'kl'
        assert board.get_piece(7, 3) == 'rl'
        assert board.get_piece(7, 0) == ''
        assert board.get_piece(7, 4) == ''

    def test_dark_kingside_castle(self):
        board = empty_board()
        board.set_piece(0, 4, 'kd')
        board.set_piece(0, 7, 'rd')
        execute_move(board, 'kd', 0, 4, 0, 6)
        assert board.get_piece(0, 6) == 'kd'
        assert board.get_piece(0, 5) == 'rd'
        assert board.get_piece(0, 7) == ''

    def test_dark_queenside_castle(self):
        board = empty_board()
        board.set_piece(0, 4, 'kd')
        board.set_piece(0, 0, 'rd')
        execute_move(board, 'kd', 0, 4, 0, 2)
        assert board.get_piece(0, 2) == 'kd'
        assert board.get_piece(0, 3) == 'rd'
        assert board.get_piece(0, 0) == ''
