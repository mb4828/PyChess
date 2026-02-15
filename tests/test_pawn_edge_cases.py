"""Tests for pawn edge cases and bugs"""
from logic.move_validator import get_valid_moves


def empty_board():
    return [['' for _ in range(8)] for _ in range(8)]


class TestPawnDoubleMoveThroughPiece:
    """BUG: Pawn can double-move by jumping over a blocking piece.
    The double-move check only verifies the destination is empty,
    not the intermediate square."""

    def test_light_pawn_cannot_jump_over_piece(self):
        """Light pawn at row 6 should NOT jump to row 4 if row 5 is blocked"""
        board = empty_board()
        board[6][4] = 'pl'
        board[5][4] = 'pd'  # blocking piece at intermediate square
        moves = get_valid_moves(board, 'pl', 6, 4)
        assert (4, 4) not in moves, "Pawn jumped over a blocking piece!"
        assert (5, 4) not in moves  # also can't move 1 forward

    def test_dark_pawn_cannot_jump_over_piece(self):
        """Dark pawn at row 1 should NOT jump to row 3 if row 2 is blocked"""
        board = empty_board()
        board[1][4] = 'pd'
        board[2][4] = 'pl'  # blocking piece at intermediate square
        moves = get_valid_moves(board, 'pd', 1, 4)
        assert (3, 4) not in moves, "Pawn jumped over a blocking piece!"
        assert (2, 4) not in moves

    def test_light_pawn_blocked_at_destination_only(self):
        """Pawn should not double-move if destination is blocked but path is clear"""
        board = empty_board()
        board[6][4] = 'pl'
        board[4][4] = 'pd'  # piece at destination
        moves = get_valid_moves(board, 'pl', 6, 4)
        assert (4, 4) not in moves
        assert (5, 4) in moves  # can still move 1 forward

    def test_dark_pawn_blocked_at_destination_only(self):
        board = empty_board()
        board[1][4] = 'pd'
        board[3][4] = 'pl'  # piece at destination
        moves = get_valid_moves(board, 'pd', 1, 4)
        assert (3, 4) not in moves
        assert (2, 4) in moves

    def test_light_pawn_double_move_path_clear(self):
        """Pawn should be able to double-move when path is fully clear"""
        board = empty_board()
        board[6][4] = 'pl'
        moves = get_valid_moves(board, 'pl', 6, 4)
        assert (4, 4) in moves
        assert (5, 4) in moves

    def test_light_pawn_jump_over_own_piece(self):
        """Light pawn should NOT jump over its own piece either"""
        board = empty_board()
        board[6][4] = 'pl'
        board[5][4] = 'pl'  # own piece blocking
        moves = get_valid_moves(board, 'pl', 6, 4)
        assert (4, 4) not in moves, "Pawn jumped over own piece!"
        assert (5, 4) not in moves
