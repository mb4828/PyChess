"""Tests for castling logic"""
from pychess.engine.move_validator import get_valid_moves
from pychess.engine.move_executor import execute_move


def empty_board():
    return [['' for _ in range(8)] for _ in range(8)]


def default_context():
    return {
        'king_moved': {'l': False, 'd': False},
        'rook_moved': {'l': {0: False, 7: False}, 'd': {0: False, 7: False}},
        'en_passant_target': None,
    }


class TestCastlingValidation:
    def test_kingside_castle_light(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        board[7][4] = ''  # remove king (simulating drag_start)
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=default_context())
        assert (7, 6) in moves

    def test_queenside_castle_light(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][0] = 'rl'
        board[7][4] = ''
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=default_context())
        assert (7, 2) in moves

    def test_kingside_castle_dark(self):
        board = empty_board()
        board[0][4] = 'kd'
        board[0][7] = 'rd'
        board[0][4] = ''
        moves = get_valid_moves(board, 'kd', 0, 4, game_context=default_context())
        assert (0, 6) in moves

    def test_queenside_castle_dark(self):
        board = empty_board()
        board[0][4] = 'kd'
        board[0][0] = 'rd'
        board[0][4] = ''
        moves = get_valid_moves(board, 'kd', 0, 4, game_context=default_context())
        assert (0, 2) in moves

    def test_cannot_castle_after_king_moved(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        board[7][4] = ''
        ctx = default_context()
        ctx['king_moved']['l'] = True
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=ctx)
        assert (7, 6) not in moves

    def test_cannot_castle_after_rook_moved(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        board[7][4] = ''
        ctx = default_context()
        ctx['rook_moved']['l'][7] = True
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=ctx)
        assert (7, 6) not in moves

    def test_cannot_castle_with_piece_in_way_kingside(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        board[7][5] = 'bl'  # bishop blocking
        board[7][4] = ''
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=default_context())
        assert (7, 6) not in moves

    def test_cannot_castle_with_piece_in_way_queenside(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][0] = 'rl'
        board[7][1] = 'nl'  # knight blocking
        board[7][4] = ''
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=default_context())
        assert (7, 2) not in moves

    def test_cannot_castle_while_in_check(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        board[0][4] = 'rd'  # rook giving check
        board[7][4] = ''
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=default_context())
        assert (7, 6) not in moves

    def test_cannot_castle_through_check(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        board[0][5] = 'rd'  # rook attacking f1 (the square king passes through)
        board[7][4] = ''
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=default_context())
        assert (7, 6) not in moves

    def test_cannot_castle_into_check(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        board[0][6] = 'rd'  # rook attacking g1 (destination)
        board[7][4] = ''
        moves = get_valid_moves(board, 'kl', 7, 4, game_context=default_context())
        assert (7, 6) not in moves

    def test_no_castling_without_context(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        board[7][4] = ''
        moves = get_valid_moves(board, 'kl', 7, 4)
        assert (7, 6) not in moves


class TestCastlingExecution:
    def test_kingside_castle_moves_rook(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][7] = 'rl'
        execute_move(board, 'kl', 7, 4, 7, 6)
        assert board[7][6] == 'kl'
        assert board[7][5] == 'rl'
        assert board[7][7] == ''
        assert board[7][4] == ''

    def test_queenside_castle_moves_rook(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[7][0] = 'rl'
        execute_move(board, 'kl', 7, 4, 7, 2)
        assert board[7][2] == 'kl'
        assert board[7][3] == 'rl'
        assert board[7][0] == ''
        assert board[7][4] == ''

    def test_dark_kingside_castle(self):
        board = empty_board()
        board[0][4] = 'kd'
        board[0][7] = 'rd'
        execute_move(board, 'kd', 0, 4, 0, 6)
        assert board[0][6] == 'kd'
        assert board[0][5] == 'rd'
        assert board[0][7] == ''

    def test_dark_queenside_castle(self):
        board = empty_board()
        board[0][4] = 'kd'
        board[0][0] = 'rd'
        execute_move(board, 'kd', 0, 4, 0, 2)
        assert board[0][2] == 'kd'
        assert board[0][3] == 'rd'
        assert board[0][0] == ''
