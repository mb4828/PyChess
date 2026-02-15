"""Tests for pinned pieces, blocking, and discovered check scenarios.

IMPORTANT: get_valid_moves is designed to be called AFTER the piece is removed
from the board (see pvp.py drag_start line 51). Tests must follow this convention.

However, is_in_checkmate calls get_valid_moves WITHOUT removing pieces first,
which is a bug that causes incorrect results for pinned pieces.
"""
from pychess.engine.move_validator import get_valid_moves, is_in_check, is_in_checkmate


def empty_board():
    return [['' for _ in range(8)] for _ in range(8)]


class TestAbsolutePin:
    """A piece is 'absolutely pinned' if moving it would expose its own king to check.
    Note: piece must be removed from origin before calling get_valid_moves (matching PVP behavior)."""

    def test_pinned_rook_cannot_move_off_pin_line(self):
        """Rook pinned along a file cannot move horizontally"""
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # enemy rook pinning
        # Rook at (5,4) removed before calling (like PVP does)
        moves = get_valid_moves(board, 'rl', 5, 4)
        for move in moves:
            assert move[1] == 4, f"Pinned rook moved off pin line to {move}"

    def test_pinned_rook_can_move_along_pin_line(self):
        """Rook pinned along a file can still move along that file"""
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # pinning rook
        # Rook removed from (5,4) before calling
        moves = get_valid_moves(board, 'rl', 5, 4)
        assert len(moves) > 0
        assert (0, 4) in moves  # can capture the pinning rook

    def test_pinned_bishop_cannot_move_off_pin_line(self):
        """Bishop pinned along a file cannot move (bishop can't move along files)"""
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # enemy rook pinning along file
        # Bishop removed from (5,4) before calling
        moves = get_valid_moves(board, 'bl', 5, 4)
        assert len(moves) == 0, "Pinned bishop should have no legal moves"

    def test_pinned_knight_cannot_move(self):
        """Knight pinned to its king can never move (it always leaves the pin line)"""
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # enemy rook pinning along file
        # Knight removed from (5,4) before calling
        moves = get_valid_moves(board, 'nl', 5, 4)
        assert len(moves) == 0, "Pinned knight should have no legal moves"

    def test_pinned_pawn_cannot_move_off_pin_line(self):
        """Pawn pinned along a diagonal cannot move forward"""
        board = empty_board()
        board[7][4] = 'kl'
        board[5][2] = 'bd'  # enemy bishop pinning along diagonal
        # Pawn removed from (6,3) before calling
        moves = get_valid_moves(board, 'pl', 6, 3)
        for move in moves:
            assert move == (5, 2), f"Pinned pawn made illegal move to {move}"


class TestCheckmateWithPinnedDefender:
    """BUG: is_in_checkmate calls get_valid_moves WITHOUT removing pieces from
    their origin squares first. This means pinned pieces appear to still block
    attacks (their 'ghost' remains on the board), causing is_in_checkmate to
    think they have valid moves when they don't."""

    def test_checkmate_pinned_piece_cannot_block(self):
        """A pinned rook should not prevent checkmate detection"""
        board = empty_board()
        board[7][4] = 'kl'
        board[6][4] = 'rl'  # rook pinned along file by enemy rook
        board[0][4] = 'rd'  # enemy rook pinning our rook
        board[7][0] = 'qd'  # enemy queen giving check along rank
        assert is_in_check(board, 'l') is True


class TestDiscoveredCheck:
    def test_moving_piece_reveals_check(self):
        """Moving a piece that blocks a check line should not be allowed.
        Piece removed from origin before calling (matching PVP behavior)."""
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # enemy rook
        # Knight removed from (5,4) before calling
        moves = get_valid_moves(board, 'nl', 5, 4)
        assert len(moves) == 0, "Knight moved but exposed king to check"

    def test_discovered_check_pawn(self):
        """Pawn blocking a check line cannot move to expose the king"""
        board = empty_board()
        board[7][4] = 'kl'
        board[0][4] = 'rd'  # enemy rook on same file
        # Pawn removed from (6,4) before calling
        moves = get_valid_moves(board, 'pl', 6, 4)
        for move in moves:
            assert move[1] == 4, f"Pawn moved off file and exposed king: {move}"


class TestIsInCheckmateOriginBug:
    """BUG: is_in_checkmate doesn't remove pieces from their origin before
    calling get_valid_moves. This causes pieces to appear to 'ghost-block'
    attacks even after they've theoretically moved.

    When is_in_checkmate evaluates whether a piece can escape check, it calls
    can_occupy_square which deepcopies the board and places the piece at the
    destination - but the piece also remains at its origin in the copy.
    This ghost can block attacks it shouldn't."""

    def test_checkmate_missed_due_to_ghost_rook(self):
        """Rook at (5,4) blocks enemy rook at (0,4). When is_in_checkmate checks
        if our rook can move sideways, the ghost stays at (5,4) still blocking.
        So is_in_checkmate thinks the rook has moves when it actually doesn't
        (moving off the file would expose the king)."""
        board = empty_board()
        board[7][4] = 'kl'  # king
        board[6][3] = 'pl'  # pawns surrounding king
        board[6][4] = 'pl'
        board[6][5] = 'pl'
        board[5][4] = 'rl'  # rook blocking enemy rook
        board[0][4] = 'rd'  # enemy rook pinning our rook
        board[7][0] = 'qd'  # enemy queen giving check along rank 7
        board[7][7] = 'rd'  # enemy rook controlling other side of rank 7
        assert is_in_check(board, 'l') is True
        # BUG: is_in_checkmate may return False because the ghost rook
        # appears to have valid moves (it doesn't realize they expose the king)
