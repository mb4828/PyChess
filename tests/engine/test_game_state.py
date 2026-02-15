"""Tests for engine/game_state.py"""
from pychess.engine.game_state import GameState


class TestGameStateInit:
    def test_starting_position(self):
        state = GameState()
        assert state.get_piece(0, 0) == 'rd'
        assert state.get_piece(0, 4) == 'kd'
        assert state.get_piece(7, 4) == 'kl'
        assert state.get_piece(1, 0) == 'pd'
        assert state.get_piece(6, 0) == 'pl'
        assert state.get_piece(4, 4) == ''

    def test_custom_board(self):
        board = [['' for _ in range(8)] for _ in range(8)]
        board[3][3] = 'kl'
        state = GameState(board=board)
        assert state.get_piece(3, 3) == 'kl'
        assert state.get_piece(0, 0) == ''

    def test_empty_factory(self):
        state = GameState.empty()
        for x in range(8):
            for y in range(8):
                assert state.get_piece(x, y) == ''


class TestGameStateAccess:
    def test_set_piece(self):
        state = GameState.empty()
        state.set_piece(4, 4, 'ql')
        assert state.get_piece(4, 4) == 'ql'

    def test_clear_square(self):
        state = GameState()
        assert state.get_piece(0, 0) == 'rd'
        state.clear_square(0, 0)
        assert state.get_piece(0, 0) == ''

    def test_is_piece_at(self):
        state = GameState()
        assert state.is_piece_at(0, 0) is True
        assert not state.is_piece_at(4, 4)

    def test_copy_is_independent(self):
        state = GameState()
        copy = state.copy()
        copy.clear_square(0, 0)
        assert state.get_piece(0, 0) == 'rd'
        assert copy.get_piece(0, 0) == ''
