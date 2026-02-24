"""Tests for logic/move_utils.py"""
from pgchess.state.game_state import GameState
from pgchess.state.move_utils import get_piece_color, is_same_color, is_piece_at, in_bounds, in_bounds_x, in_bounds_y


def empty_board() -> GameState:
    """Return a fresh empty GameState for test setup."""
    return GameState.empty()


class TestGetPieceColor:
    """Tests for get_piece_color with piece codes and bare color strings."""

    def test_light_pawn(self):
        """'pl' should return 'l'."""
        assert get_piece_color('pl') == 'l'

    def test_dark_pawn(self):
        """'pd' should return 'd'."""
        assert get_piece_color('pd') == 'd'

    def test_light_king(self):
        """'kl' should return 'l'."""
        assert get_piece_color('kl') == 'l'

    def test_dark_queen(self):
        """'qd' should return 'd'."""
        assert get_piece_color('qd') == 'd'

    def test_color_string_light(self):
        """A bare 'l' color string should return 'l'."""
        assert get_piece_color('l') == 'l'

    def test_color_string_dark(self):
        """A bare 'd' color string should return 'd'."""
        assert get_piece_color('d') == 'd'

    def test_light_knight(self):
        """'nl' should return 'l'."""
        assert get_piece_color('nl') == 'l'

    def test_dark_bishop(self):
        """'bd' should return 'd'."""
        assert get_piece_color('bd') == 'd'


class TestIsSameColor:
    """Tests for is_same_color comparing two piece codes."""

    def test_same_light(self):
        """Two light pieces should be considered the same color."""
        assert is_same_color('pl', 'kl') is True

    def test_same_dark(self):
        """Two dark pieces should be considered the same color."""
        assert is_same_color('pd', 'kd') is True

    def test_different(self):
        """A light and a dark piece should not be considered the same color."""
        assert is_same_color('pl', 'pd') is False

    def test_different_reversed(self):
        """Order should not matter for opposite-color comparison."""
        assert is_same_color('kd', 'rl') is False


class TestIsPieceAt:
    """Tests for is_piece_at on empty, occupied, and marker squares."""

    def test_empty_square(self):
        """An empty square should return False."""
        board = empty_board()
        assert not is_piece_at(board, 3, 3)

    def test_piece_present(self):
        """A square with a piece should return True."""
        board = empty_board()
        board.set_piece(3, 3, 'pl')
        assert is_piece_at(board, 3, 3) is True

    def test_en_passant_marker(self):
        """An en passant marker (+ep) should not be treated as a piece."""
        board = empty_board()
        board.set_piece(3, 3, '+ep')
        assert is_piece_at(board, 3, 3) is False


class TestInBounds:
    """Tests for in_bounds, in_bounds_x, and in_bounds_y boundary checks."""

    def test_valid_positions(self):
        """All indices 0-7 should be considered in-bounds."""
        for i in range(8):
            assert in_bounds_x(i) is True
            assert in_bounds_y(i) is True

    def test_negative(self):
        """Negative indices should be out of bounds."""
        assert in_bounds_x(-1) is False
        assert in_bounds_y(-1) is False

    def test_too_large(self):
        """Index 8 should be out of bounds."""
        assert in_bounds_x(8) is False
        assert in_bounds_y(8) is False

    def test_in_bounds_combined(self):
        """in_bounds should return True for corners and False when either coord is invalid."""
        assert in_bounds(0, 0) is True
        assert in_bounds(7, 7) is True
        assert in_bounds(-1, 0) is False
        assert in_bounds(0, 8) is False
