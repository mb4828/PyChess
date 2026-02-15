"""Tests for basic piece movement validation"""
from logic.move_validator import get_valid_moves


def empty_board():
    return [['' for _ in range(8)] for _ in range(8)]


class TestKingMoves:
    def test_king_center_of_empty_board(self):
        board = empty_board()
        board[4][4] = 'kl'
        moves = get_valid_moves(board, 'kl', 4, 4)
        assert len(moves) == 8
        expected = {(3, 3), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)}
        assert set(moves) == expected

    def test_king_corner(self):
        board = empty_board()
        board[0][0] = 'kl'
        moves = get_valid_moves(board, 'kl', 0, 0)
        expected = {(0, 1), (1, 0), (1, 1)}
        assert set(moves) == expected

    def test_king_blocked_by_own_pieces(self):
        board = empty_board()
        board[0][0] = 'kl'
        board[0][1] = 'pl'
        board[1][0] = 'pl'
        board[1][1] = 'pl'
        moves = get_valid_moves(board, 'kl', 0, 0)
        assert len(moves) == 0

    def test_king_can_capture_enemy(self):
        board = empty_board()
        board[4][4] = 'kl'
        board[4][5] = 'pd'
        moves = get_valid_moves(board, 'kl', 4, 4)
        assert (4, 5) in moves


class TestQueenMoves:
    def test_queen_center_of_empty_board(self):
        board = empty_board()
        board[4][4] = 'ql'
        moves = get_valid_moves(board, 'ql', 4, 4)
        # Queen should reach all horizontal, vertical, and diagonal squares
        assert len(moves) == 27

    def test_queen_blocked_by_own_piece(self):
        board = empty_board()
        board[4][4] = 'ql'
        board[4][5] = 'pl'
        moves = get_valid_moves(board, 'ql', 4, 4)
        assert (4, 5) not in moves
        assert (4, 6) not in moves

    def test_queen_can_capture_then_stop(self):
        board = empty_board()
        board[4][4] = 'ql'
        board[4][6] = 'pd'
        moves = get_valid_moves(board, 'ql', 4, 4)
        assert (4, 5) in moves
        assert (4, 6) in moves  # capture
        assert (4, 7) not in moves  # blocked after capture


class TestBishopMoves:
    def test_bishop_center_of_empty_board(self):
        board = empty_board()
        board[4][4] = 'bl'
        moves = get_valid_moves(board, 'bl', 4, 4)
        assert len(moves) == 13

    def test_bishop_blocked_by_own_piece(self):
        board = empty_board()
        board[4][4] = 'bl'
        board[5][5] = 'pl'
        moves = get_valid_moves(board, 'bl', 4, 4)
        assert (5, 5) not in moves
        assert (6, 6) not in moves


class TestRookMoves:
    def test_rook_center_of_empty_board(self):
        board = empty_board()
        board[4][4] = 'rl'
        moves = get_valid_moves(board, 'rl', 4, 4)
        assert len(moves) == 14

    def test_rook_corner(self):
        board = empty_board()
        board[0][0] = 'rl'
        moves = get_valid_moves(board, 'rl', 0, 0)
        assert len(moves) == 14

    def test_rook_blocked_by_own_piece(self):
        board = empty_board()
        board[4][4] = 'rl'
        board[4][6] = 'pl'
        moves = get_valid_moves(board, 'rl', 4, 4)
        assert (4, 5) in moves
        assert (4, 6) not in moves
        assert (4, 7) not in moves


class TestKnightMoves:
    def test_knight_center_of_empty_board(self):
        board = empty_board()
        board[4][4] = 'nl'
        moves = get_valid_moves(board, 'nl', 4, 4)
        expected = {(2, 3), (2, 5), (3, 2), (3, 6), (5, 2), (5, 6), (6, 3), (6, 5)}
        assert set(moves) == expected

    def test_knight_corner(self):
        board = empty_board()
        board[0][0] = 'nl'
        moves = get_valid_moves(board, 'nl', 0, 0)
        expected = {(1, 2), (2, 1)}
        assert set(moves) == expected

    def test_knight_jumps_over_pieces(self):
        board = empty_board()
        board[4][4] = 'nl'
        # surround with own pieces
        board[3][3] = 'pl'
        board[3][4] = 'pl'
        board[3][5] = 'pl'
        board[4][3] = 'pl'
        board[4][5] = 'pl'
        board[5][3] = 'pl'
        board[5][4] = 'pl'
        board[5][5] = 'pl'
        moves = get_valid_moves(board, 'nl', 4, 4)
        # Knight should still reach all 8 L-shaped squares
        assert len(moves) == 8

    def test_knight_blocked_by_own_piece_at_destination(self):
        board = empty_board()
        board[4][4] = 'nl'
        board[2][3] = 'pl'  # own piece at one destination
        moves = get_valid_moves(board, 'nl', 4, 4)
        assert (2, 3) not in moves
        assert len(moves) == 7


class TestPawnMoves:
    def test_light_pawn_initial_position(self):
        board = empty_board()
        board[6][4] = 'pl'
        moves = get_valid_moves(board, 'pl', 6, 4)
        assert (5, 4) in moves  # 1 forward
        assert (4, 4) in moves  # 2 forward

    def test_dark_pawn_initial_position(self):
        board = empty_board()
        board[1][4] = 'pd'
        moves = get_valid_moves(board, 'pd', 1, 4)
        assert (2, 4) in moves  # 1 forward
        assert (3, 4) in moves  # 2 forward

    def test_light_pawn_non_initial(self):
        board = empty_board()
        board[5][4] = 'pl'
        moves = get_valid_moves(board, 'pl', 5, 4)
        assert (4, 4) in moves
        assert (3, 4) not in moves  # can't double move

    def test_dark_pawn_non_initial(self):
        board = empty_board()
        board[2][4] = 'pd'
        moves = get_valid_moves(board, 'pd', 2, 4)
        assert (3, 4) in moves
        assert (4, 4) not in moves  # can't double move

    def test_pawn_capture_diagonal(self):
        board = empty_board()
        board[5][4] = 'pl'
        board[4][3] = 'pd'  # enemy piece
        board[4][5] = 'pd'  # enemy piece
        moves = get_valid_moves(board, 'pl', 5, 4)
        assert (4, 3) in moves
        assert (4, 5) in moves
        assert (4, 4) in moves  # can still move forward

    def test_pawn_cannot_capture_forward(self):
        board = empty_board()
        board[5][4] = 'pl'
        board[4][4] = 'pd'  # blocked
        moves = get_valid_moves(board, 'pl', 5, 4)
        assert (4, 4) not in moves

    def test_pawn_cannot_capture_own_piece_diagonal(self):
        board = empty_board()
        board[5][4] = 'pl'
        board[4][3] = 'pl'  # own piece
        moves = get_valid_moves(board, 'pl', 5, 4)
        assert (4, 3) not in moves

    def test_pawn_at_edge_of_board(self):
        board = empty_board()
        board[5][0] = 'pl'
        moves = get_valid_moves(board, 'pl', 5, 0)
        # Should not crash from checking y=-1
        assert (4, 0) in moves

    def test_dark_pawn_capture_diagonal(self):
        board = empty_board()
        board[2][4] = 'pd'
        board[3][3] = 'pl'
        board[3][5] = 'pl'
        moves = get_valid_moves(board, 'pd', 2, 4)
        assert (3, 3) in moves
        assert (3, 5) in moves
