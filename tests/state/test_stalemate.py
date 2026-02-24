"""Tests for stalemate detection"""
from pgchess.state.game_state import GameState
from pgchess.state.move_validator import is_in_stalemate, is_in_checkmate


def empty_board() -> GameState:
    """Return a fresh empty GameState for test setup."""
    return GameState.empty()


class TestStalemate:
    """Tests for is_in_stalemate across various board configurations."""

    def test_basic_stalemate(self):
        """King has no legal moves and is not in check"""
        board = empty_board()
        board.set_piece(0, 0, 'kd')
        board.set_piece(1, 2, 'ql')  # queen controls row 1 and column 2
        board.set_piece(2, 1, 'kl')  # king controls (1,0), (1,1), (1,2)
        assert is_in_stalemate(board, 'd') is True
        assert is_in_checkmate(board, 'd') is False

    def test_not_stalemate_when_in_check(self):
        """King is in check - this is not stalemate"""
        board = empty_board()
        board.set_piece(0, 0, 'kd')
        board.set_piece(0, 7, 'rl')  # rook giving check
        board.set_piece(7, 4, 'kl')
        assert is_in_stalemate(board, 'd') is False

    def test_not_stalemate_with_legal_moves(self):
        """King has legal moves - not stalemate"""
        board = empty_board()
        board.set_piece(4, 4, 'kd')
        board.set_piece(7, 0, 'kl')
        assert is_in_stalemate(board, 'd') is False

    def test_stalemate_king_cornered_by_queen(self):
        """Classic stalemate: light king in corner with queen cutting off all escape squares."""
        board = empty_board()
        board.set_piece(0, 0, 'kl')
        board.set_piece(2, 1, 'qd')  # queen at (2,1) attacks (1,0), (1,1), (0,1)
        board.set_piece(7, 7, 'kd')
        # king at (0,0): can go (0,1) attacked by queen, (1,0) attacked by queen, (1,1) attacked by queen
        assert is_in_stalemate(board, 'l') is True

    def test_not_stalemate_other_pieces_can_move(self):
        """King is boxed in but another piece can still move"""
        board = empty_board()
        board.set_piece(0, 0, 'kd')
        board.set_piece(1, 2, 'ql')
        board.set_piece(2, 1, 'kl')
        board.set_piece(5, 5, 'pd')  # dark pawn can still move
        assert is_in_stalemate(board, 'd') is False

    def test_stalemate_is_not_checkmate(self):
        """Ensure stalemate and checkmate are mutually exclusive"""
        board = empty_board()
        board.set_piece(0, 0, 'kl')
        board.set_piece(2, 1, 'qd')
        board.set_piece(7, 7, 'kd')
        assert is_in_stalemate(board, 'l') is True
        assert is_in_checkmate(board, 'l') is False
