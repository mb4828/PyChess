"""Tests for logic/move_executor.py"""
from pychess.state.game_state import GameState
from pychess.state.move_executor import execute_move


def empty_board() -> GameState:
    return GameState.empty()


class TestExecuteMove:
    def test_places_piece_at_destination(self):
        board = empty_board()
        board.set_piece(6, 4, 'pl')
        result = execute_move(board, 'pl', 6, 4, 5, 4)
        assert result.get_piece(5, 4) == 'pl'

    def test_clears_origin(self):
        board = empty_board()
        board.set_piece(6, 4, 'pl')
        result = execute_move(board, 'pl', 6, 4, 5, 4)
        assert result.get_piece(6, 4) == ''

    def test_captures_enemy_piece(self):
        board = empty_board()
        board.set_piece(5, 4, 'pl')
        board.set_piece(4, 3, 'pd')
        result = execute_move(board, 'pl', 5, 4, 4, 3)
        assert result.get_piece(4, 3) == 'pl'
        assert result.get_piece(5, 4) == ''

    def test_mutates_original_board(self):
        """execute_move modifies the board in place (not a copy)"""
        board = empty_board()
        board.set_piece(6, 4, 'pl')
        original_ref = board
        result = execute_move(board, 'pl', 6, 4, 5, 4)
        assert result is original_ref
