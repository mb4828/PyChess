"""Tests for logic/move_utils.py"""
from logic.move_utils import get_piece_color, is_same_color, is_piece_at, in_bounds, in_bounds_x, in_bounds_y


def empty_board():
    return [['' for _ in range(8)] for _ in range(8)]


class TestGetPieceColor:
    def test_light_pawn(self):
        assert get_piece_color('pl') == 'l'

    def test_dark_pawn(self):
        assert get_piece_color('pd') == 'd'

    def test_light_king(self):
        assert get_piece_color('kl') == 'l'

    def test_dark_queen(self):
        assert get_piece_color('qd') == 'd'

    def test_color_string_light(self):
        assert get_piece_color('l') == 'l'

    def test_color_string_dark(self):
        assert get_piece_color('d') == 'd'

    def test_light_knight(self):
        assert get_piece_color('nl') == 'l'

    def test_dark_bishop(self):
        assert get_piece_color('bd') == 'd'


class TestIsSameColor:
    def test_same_light(self):
        assert is_same_color('pl', 'kl') is True

    def test_same_dark(self):
        assert is_same_color('pd', 'kd') is True

    def test_different(self):
        assert is_same_color('pl', 'pd') is False

    def test_different_reversed(self):
        assert is_same_color('kd', 'rl') is False


class TestIsPieceAt:
    def test_empty_square(self):
        board = empty_board()
        assert not is_piece_at(board, 3, 3)

    def test_piece_present(self):
        board = empty_board()
        board[3][3] = 'pl'
        assert is_piece_at(board, 3, 3) is True

    def test_en_passant_marker(self):
        board = empty_board()
        board[3][3] = '+ep'
        assert is_piece_at(board, 3, 3) is False


class TestInBounds:
    def test_valid_positions(self):
        for i in range(8):
            assert in_bounds_x(i) is True
            assert in_bounds_y(i) is True

    def test_negative(self):
        assert in_bounds_x(-1) is False
        assert in_bounds_y(-1) is False

    def test_too_large(self):
        assert in_bounds_x(8) is False
        assert in_bounds_y(8) is False

    def test_in_bounds_combined(self):
        assert in_bounds(0, 0) is True
        assert in_bounds(7, 7) is True
        assert in_bounds(-1, 0) is False
        assert in_bounds(0, 8) is False
