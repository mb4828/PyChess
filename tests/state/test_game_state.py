"""Tests for engine/game_state.py"""
from pgchess.state.game_state import GameState


class TestGameStateInit:
    """Tests for GameState construction and factory methods."""

    def test_starting_position(self):
        """Default constructor should produce the standard chess starting position."""
        state = GameState()
        assert state.get_piece(0, 0) == 'rd'
        assert state.get_piece(0, 4) == 'kd'
        assert state.get_piece(7, 4) == 'kl'
        assert state.get_piece(1, 0) == 'pd'
        assert state.get_piece(6, 0) == 'pl'
        assert state.get_piece(4, 4) == ''

    def test_custom_board(self):
        """Passing a pre-built board array should use that layout directly."""
        board = [['' for _ in range(8)] for _ in range(8)]
        board[3][3] = 'kl'
        state = GameState(board=board)
        assert state.get_piece(3, 3) == 'kl'
        assert state.get_piece(0, 0) == ''

    def test_empty_factory(self):
        """GameState.empty() should produce a board with no pieces on any square."""
        state = GameState.empty()
        for x in range(8):
            for y in range(8):
                assert state.get_piece(x, y) == ''


class TestGameStateAccess:
    """Tests for GameState piece manipulation and querying methods."""

    def test_set_piece(self):
        """set_piece should place the given piece code at the specified square."""
        state = GameState.empty()
        state.set_piece(4, 4, 'ql')
        assert state.get_piece(4, 4) == 'ql'

    def test_clear_square(self):
        """clear_square should remove any piece at the specified square."""
        state = GameState()
        assert state.get_piece(0, 0) == 'rd'
        state.clear_square(0, 0)
        assert state.get_piece(0, 0) == ''

    def test_is_piece_at(self):
        """is_piece_at should return True for occupied squares and False for empty ones."""
        state = GameState()
        assert state.is_piece_at(0, 0) is True
        assert not state.is_piece_at(4, 4)

    def test_copy_is_independent(self):
        """copy() should return a deep copy so mutations do not affect the original."""
        state = GameState()
        copy = state.copy()
        copy.clear_square(0, 0)
        assert state.get_piece(0, 0) == 'rd'
        assert copy.get_piece(0, 0) == ''
