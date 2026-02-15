"""Tests for check and checkmate logic"""
from pychess.engine.move_validator import is_in_check, is_in_checkmate, get_valid_moves


def empty_board():
    return [['' for _ in range(8)] for _ in range(8)]


class TestIsInCheck:
    def test_not_in_check(self):
        board = empty_board()
        board[7][4] = 'kl'
        assert is_in_check(board, 'l') is False

    def test_in_check_by_rook(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # rook on same file
        assert is_in_check(board, 'l') is True

    def test_in_check_by_bishop(self):
        board = empty_board()
        board[4][4] = 'kl'
        board[2][2] = 'bd'  # bishop on diagonal
        assert is_in_check(board, 'l') is True

    def test_in_check_by_queen(self):
        board = empty_board()
        board[4][4] = 'kl'
        board[4][7] = 'qd'  # queen on same rank
        assert is_in_check(board, 'l') is True

    def test_in_check_by_knight(self):
        board = empty_board()
        board[4][4] = 'kl'
        board[2][3] = 'nd'  # knight attacking
        assert is_in_check(board, 'l') is True

    def test_in_check_by_pawn(self):
        board = empty_board()
        board[4][4] = 'kl'
        board[3][3] = 'pd'  # dark pawn attacks diagonally downward
        assert is_in_check(board, 'l') is True

    def test_not_in_check_blocked_by_piece(self):
        board = empty_board()
        board[7][4] = 'kl'
        board[5][4] = 'pl'  # own piece blocks
        board[0][4] = 'rd'  # rook on same file but blocked
        assert is_in_check(board, 'l') is False

    def test_dark_king_in_check(self):
        board = empty_board()
        board[0][4] = 'kd'
        board[7][4] = 'rl'  # rook on same file
        assert is_in_check(board, 'd') is True

    def test_accepts_piece_code_or_color(self):
        board = empty_board()
        board[4][4] = 'kl'
        board[0][4] = 'rd'
        assert is_in_check(board, 'l') is True
        assert is_in_check(board, 'pl') is True  # should also work with piece code


class TestKingCannotMoveIntoCheck:
    """King must be removed from origin before calling get_valid_moves (matching PVP)."""

    def test_king_cannot_move_into_rook_line(self):
        board = empty_board()
        board[0][5] = 'rd'  # rook controls column 5
        # King removed from (4,4) before calling
        moves = get_valid_moves(board, 'kl', 4, 4)
        assert (4, 5) not in moves
        assert (3, 5) not in moves
        assert (5, 5) not in moves

    def test_king_cannot_move_adjacent_to_enemy_king(self):
        board = empty_board()
        board[4][6] = 'kd'
        # King removed from (4,4) before calling
        moves = get_valid_moves(board, 'kl', 4, 4)
        assert (4, 5) not in moves  # between the two kings

    def test_king_can_capture_undefended_attacker(self):
        board = empty_board()
        board[4][5] = 'rd'  # undefended rook
        # King removed from (4,4) before calling
        moves = get_valid_moves(board, 'kl', 4, 4)
        assert (4, 5) in moves  # can capture

    def test_king_cannot_capture_defended_piece(self):
        board = empty_board()
        board[4][5] = 'rd'  # rook defended by another rook
        board[4][7] = 'rd'
        # King removed from (4,4) before calling
        moves = get_valid_moves(board, 'kl', 4, 4)
        assert (4, 5) not in moves  # capturing puts king in check from other rook


class TestCheckmate:
    def test_back_rank_mate(self):
        """Classic back rank mate: king trapped by own pawns, rook delivers check.
        BUG: This fails because is_in_checkmate has the ghost-piece bug — the king's
        ghost at its origin blocks the rook, making (7,7) look safe when it isn't."""
        board = empty_board()
        board[7][6] = 'kl'  # king at g1
        board[6][5] = 'pl'  # pawns at f2, g2, h2
        board[6][6] = 'pl'
        board[6][7] = 'pl'
        board[7][0] = 'rd'  # rook gives check on rank 7
        assert is_in_check(board, 'l') is True
        assert is_in_checkmate(board, 'l') is True

    def test_not_checkmate_can_block(self):
        """King is in check but a piece can block"""
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # rook gives check
        board[5][2] = 'rl'  # own rook can block by moving to (5,4)
        assert is_in_check(board, 'l') is True
        assert is_in_checkmate(board, 'l') is False

    def test_not_checkmate_can_capture_attacker(self):
        """King is in check but another piece can capture the attacker"""
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # rook gives check
        board[0][0] = 'rl'  # own rook can capture the attacker
        assert is_in_check(board, 'l') is True
        assert is_in_checkmate(board, 'l') is False

    def test_not_checkmate_king_can_escape(self):
        """King is in check but can move out of danger"""
        board = empty_board()
        board[4][4] = 'kl'
        board[0][4] = 'rd'  # rook gives check on file
        assert is_in_check(board, 'l') is True
        assert is_in_checkmate(board, 'l') is False  # king can move sideways


class TestStalemate:
    """BUG: is_in_checkmate returns True for stalemate positions.
    Stalemate should be a draw, not a win."""

    def test_stalemate_is_not_checkmate(self):
        """King is not in check but has no legal moves - this is stalemate, not checkmate"""
        board = empty_board()
        board[0][0] = 'kl'  # light king in corner
        board[2][1] = 'qd'  # queen controls escape squares
        board[1][2] = 'kd'  # dark king covers remaining squares
        assert is_in_check(board, 'l') is False, "King should not be in check in stalemate"
        # BUG: This should be False (stalemate is not checkmate) but the code returns True
        assert is_in_checkmate(board, 'l') is False, \
            "Stalemate should not be treated as checkmate! This is a draw."

    def test_stalemate_king_only_vs_king_queen(self):
        """Classic stalemate: lone king in corner with no legal moves but not in check"""
        board = empty_board()
        board[0][0] = 'kl'
        board[1][2] = 'qd'  # controls row 1 and nearby squares
        board[2][0] = 'kd'  # controls (1,0), (1,1)
        assert is_in_check(board, 'l') is False
        assert is_in_checkmate(board, 'l') is False, \
            "Stalemate is a draw, not checkmate"
