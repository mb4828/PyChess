"""Tests for en passant logic"""
from pychess.state.move_validator import get_valid_moves
from pychess.state.move_executor import execute_move


def empty_board():
    return [['' for _ in range(8)] for _ in range(8)]


def default_context():
    return {
        'king_moved': {'l': False, 'd': False},
        'rook_moved': {'l': {0: False, 7: False}, 'd': {0: False, 7: False}},
        'en_passant_target': None,
    }


class TestEnPassantValidation:
    def test_light_pawn_en_passant_left(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'kd'
        board[3][4] = 'pl'  # light pawn on row 3
        board[3][3] = 'pd'  # dark pawn just moved 2 squares to land here
        board[3][4] = ''  # simulating drag_start
        ctx = default_context()
        ctx['en_passant_target'] = (2, 3)  # the square the dark pawn skipped
        moves = get_valid_moves(board, 'pl', 3, 4, game_context=ctx)
        assert (2, 3) in moves

    def test_light_pawn_en_passant_right(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'kd'
        board[3][4] = 'pl'
        board[3][5] = 'pd'
        board[3][4] = ''
        ctx = default_context()
        ctx['en_passant_target'] = (2, 5)
        moves = get_valid_moves(board, 'pl', 3, 4, game_context=ctx)
        assert (2, 5) in moves

    def test_dark_pawn_en_passant(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'kd'
        board[4][3] = 'pd'  # dark pawn on row 4
        board[4][4] = 'pl'  # light pawn just moved 2 squares
        board[4][3] = ''
        ctx = default_context()
        ctx['en_passant_target'] = (5, 4)
        moves = get_valid_moves(board, 'pd', 4, 3, game_context=ctx)
        assert (5, 4) in moves

    def test_no_en_passant_without_target(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'kd'
        board[3][4] = 'pl'
        board[3][3] = 'pd'
        board[3][4] = ''
        ctx = default_context()
        ctx['en_passant_target'] = None
        moves = get_valid_moves(board, 'pl', 3, 4, game_context=ctx)
        assert (2, 3) not in moves

    def test_no_en_passant_wrong_row_light(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'kd'
        board[4][4] = 'pl'  # wrong row for light en passant (should be row 3)
        board[4][4] = ''
        ctx = default_context()
        ctx['en_passant_target'] = (3, 3)
        moves = get_valid_moves(board, 'pl', 4, 4, game_context=ctx)
        assert (3, 3) not in moves

    def test_no_en_passant_too_far(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'kd'
        board[3][4] = 'pl'
        board[3][4] = ''
        ctx = default_context()
        ctx['en_passant_target'] = (2, 6)  # too far away
        moves = get_valid_moves(board, 'pl', 3, 4, game_context=ctx)
        assert (2, 6) not in moves


class TestEnPassantExecution:
    def test_en_passant_removes_captured_pawn_light(self):
        board = empty_board()
        board[3][4] = 'pl'
        board[3][3] = 'pd'  # the pawn to be captured
        execute_move(board, 'pl', 3, 4, 2, 3, is_en_passant=True)
        assert board[2][3] == 'pl'  # pawn moved to en passant square
        assert board[3][4] == ''    # origin cleared
        assert board[3][3] == ''    # captured pawn removed

    def test_en_passant_removes_captured_pawn_dark(self):
        board = empty_board()
        board[4][3] = 'pd'
        board[4][4] = 'pl'  # the pawn to be captured
        execute_move(board, 'pd', 4, 3, 5, 4, is_en_passant=True)
        assert board[5][4] == 'pd'  # pawn moved to en passant square
        assert board[4][3] == ''    # origin cleared
        assert board[4][4] == ''    # captured pawn removed

    def test_normal_capture_not_en_passant(self):
        board = empty_board()
        board[3][4] = 'pl'
        board[2][3] = 'pd'  # normal diagonal capture target
        execute_move(board, 'pl', 3, 4, 2, 3, is_en_passant=False)
        assert board[2][3] == 'pl'
        assert board[3][4] == ''
