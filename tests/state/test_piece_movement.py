"""Tests for basic piece movement validation"""
from pgchess.state.game_context import GameContext
from pgchess.state.game_state import GameState
from pgchess.state.move_validator import get_valid_moves


def empty_board() -> GameState:
    """Return a fresh empty GameState for test setup."""
    return GameState.empty()


class TestKingMoves:
    """Tests for king move generation."""

    def test_king_center_of_empty_board(self):
        """King in the center of an empty board should have exactly 8 moves."""
        board = empty_board()
        board.set_piece(4, 4, 'kl')
        moves = get_valid_moves(board, GameContext(), 'kl', 4, 4)
        assert len(moves) == 8
        expected = {(3, 3), (3, 4), (3, 5), (4, 3),
                    (4, 5), (5, 3), (5, 4), (5, 5)}
        assert set(moves) == expected

    def test_king_corner(self):
        """King in a corner should have exactly 3 moves."""
        board = empty_board()
        board.set_piece(0, 0, 'kl')
        moves = get_valid_moves(board, GameContext(), 'kl', 0, 0)
        expected = {(0, 1), (1, 0), (1, 1)}
        assert set(moves) == expected

    def test_king_blocked_by_own_pieces(self):
        """King fully surrounded by own pieces should have no legal moves."""
        board = empty_board()
        board.set_piece(0, 0, 'kl')
        board.set_piece(0, 1, 'pl')
        board.set_piece(1, 0, 'pl')
        board.set_piece(1, 1, 'pl')
        moves = get_valid_moves(board, GameContext(), 'kl', 0, 0)
        assert len(moves) == 0

    def test_king_can_capture_enemy(self):
        """King should be able to capture an adjacent undefended enemy piece."""
        board = empty_board()
        board.set_piece(4, 4, 'kl')
        board.set_piece(4, 5, 'pd')
        moves = get_valid_moves(board, GameContext(), 'kl', 4, 4)
        assert (4, 5) in moves


class TestQueenMoves:
    """Tests for queen move generation."""

    def test_queen_center_of_empty_board(self):
        """Queen in the center of an empty board should have exactly 27 moves."""
        board = empty_board()
        board.set_piece(4, 4, 'ql')
        moves = get_valid_moves(board, GameContext(), 'ql', 4, 4)
        # Queen should reach all horizontal, vertical, and diagonal squares
        assert len(moves) == 27

    def test_queen_blocked_by_own_piece(self):
        """Queen should not slide through or onto a square occupied by own piece."""
        board = empty_board()
        board.set_piece(4, 4, 'ql')
        board.set_piece(4, 5, 'pl')
        moves = get_valid_moves(board, GameContext(), 'ql', 4, 4)
        assert (4, 5) not in moves
        assert (4, 6) not in moves

    def test_queen_can_capture_then_stop(self):
        """Queen should stop after capturing an enemy piece and not slide further."""
        board = empty_board()
        board.set_piece(4, 4, 'ql')
        board.set_piece(4, 6, 'pd')
        moves = get_valid_moves(board, GameContext(), 'ql', 4, 4)
        assert (4, 5) in moves
        assert (4, 6) in moves  # capture
        assert (4, 7) not in moves  # blocked after capture


class TestBishopMoves:
    """Tests for bishop move generation."""

    def test_bishop_center_of_empty_board(self):
        """Bishop in the center of an empty board should have exactly 13 moves."""
        board = empty_board()
        board.set_piece(4, 4, 'bl')
        moves = get_valid_moves(board, GameContext(), 'bl', 4, 4)
        assert len(moves) == 13

    def test_bishop_blocked_by_own_piece(self):
        """Bishop should not slide through or onto a square occupied by own piece."""
        board = empty_board()
        board.set_piece(4, 4, 'bl')
        board.set_piece(5, 5, 'pl')
        moves = get_valid_moves(board, GameContext(), 'bl', 4, 4)
        assert (5, 5) not in moves
        assert (6, 6) not in moves


class TestRookMoves:
    """Tests for rook move generation."""

    def test_rook_center_of_empty_board(self):
        """Rook in the center of an empty board should have exactly 14 moves."""
        board = empty_board()
        board.set_piece(4, 4, 'rl')
        moves = get_valid_moves(board, GameContext(), 'rl', 4, 4)
        assert len(moves) == 14

    def test_rook_corner(self):
        """Rook in a corner should still have exactly 14 moves."""
        board = empty_board()
        board.set_piece(0, 0, 'rl')
        moves = get_valid_moves(board, GameContext(), 'rl', 0, 0)
        assert len(moves) == 14

    def test_rook_blocked_by_own_piece(self):
        """Rook should stop before a square occupied by own piece."""
        board = empty_board()
        board.set_piece(4, 4, 'rl')
        board.set_piece(4, 6, 'pl')
        moves = get_valid_moves(board, GameContext(), 'rl', 4, 4)
        assert (4, 5) in moves
        assert (4, 6) not in moves
        assert (4, 7) not in moves


class TestKnightMoves:
    """Tests for knight move generation."""

    def test_knight_center_of_empty_board(self):
        """Knight in the center of an empty board should have all 8 L-shape moves."""
        board = empty_board()
        board.set_piece(4, 4, 'nl')
        moves = get_valid_moves(board, GameContext(), 'nl', 4, 4)
        expected = {(2, 3), (2, 5), (3, 2), (3, 6),
                    (5, 2), (5, 6), (6, 3), (6, 5)}
        assert set(moves) == expected

    def test_knight_corner(self):
        """Knight in a corner should have exactly 2 moves."""
        board = empty_board()
        board.set_piece(0, 0, 'nl')
        moves = get_valid_moves(board, GameContext(), 'nl', 0, 0)
        expected = {(1, 2), (2, 1)}
        assert set(moves) == expected

    def test_knight_jumps_over_pieces(self):
        """Knight should ignore all pieces between itself and its L-shape destinations."""
        board = empty_board()
        board.set_piece(4, 4, 'nl')
        # surround with own pieces
        board.set_piece(3, 3, 'pl')
        board.set_piece(3, 4, 'pl')
        board.set_piece(3, 5, 'pl')
        board.set_piece(4, 3, 'pl')
        board.set_piece(4, 5, 'pl')
        board.set_piece(5, 3, 'pl')
        board.set_piece(5, 4, 'pl')
        board.set_piece(5, 5, 'pl')
        moves = get_valid_moves(board, GameContext(), 'nl', 4, 4)
        # Knight should still reach all 8 L-shaped squares
        assert len(moves) == 8

    def test_knight_blocked_by_own_piece_at_destination(self):
        """Knight should not land on a square occupied by own piece."""
        board = empty_board()
        board.set_piece(4, 4, 'nl')
        board.set_piece(2, 3, 'pl')  # own piece at one destination
        moves = get_valid_moves(board, GameContext(), 'nl', 4, 4)
        assert (2, 3) not in moves
        assert len(moves) == 7


class TestPawnMoves:
    """Tests for pawn move generation including forward advances and diagonal captures."""

    def test_light_pawn_initial_position(self):
        """Light pawn on starting rank should be able to advance one or two squares."""
        board = empty_board()
        board.set_piece(6, 4, 'pl')
        moves = get_valid_moves(board, GameContext(), 'pl', 6, 4)
        assert (5, 4) in moves  # 1 forward
        assert (4, 4) in moves  # 2 forward

    def test_dark_pawn_initial_position(self):
        """Dark pawn on starting rank should be able to advance one or two squares."""
        board = empty_board()
        board.set_piece(1, 4, 'pd')
        moves = get_valid_moves(board, GameContext(), 'pd', 1, 4)
        assert (2, 4) in moves  # 1 forward
        assert (3, 4) in moves  # 2 forward

    def test_light_pawn_non_initial(self):
        """Light pawn not on starting rank should only advance one square."""
        board = empty_board()
        board.set_piece(5, 4, 'pl')
        moves = get_valid_moves(board, GameContext(), 'pl', 5, 4)
        assert (4, 4) in moves
        assert (3, 4) not in moves  # can't double move

    def test_dark_pawn_non_initial(self):
        """Dark pawn not on starting rank should only advance one square."""
        board = empty_board()
        board.set_piece(2, 4, 'pd')
        moves = get_valid_moves(board, GameContext(), 'pd', 2, 4)
        assert (3, 4) in moves
        assert (4, 4) not in moves  # can't double move

    def test_pawn_capture_diagonal(self):
        """Pawn should be able to capture diagonally while still advancing forward."""
        board = empty_board()
        board.set_piece(5, 4, 'pl')
        board.set_piece(4, 3, 'pd')  # enemy piece
        board.set_piece(4, 5, 'pd')  # enemy piece
        moves = get_valid_moves(board, GameContext(), 'pl', 5, 4)
        assert (4, 3) in moves
        assert (4, 5) in moves
        assert (4, 4) in moves  # can still move forward

    def test_pawn_cannot_capture_forward(self):
        """Pawn must not capture directly forward — only diagonally."""
        board = empty_board()
        board.set_piece(5, 4, 'pl')
        board.set_piece(4, 4, 'pd')  # blocked
        moves = get_valid_moves(board, GameContext(), 'pl', 5, 4)
        assert (4, 4) not in moves

    def test_pawn_cannot_capture_own_piece_diagonal(self):
        """Pawn must not move diagonally onto a square occupied by own piece."""
        board = empty_board()
        board.set_piece(5, 4, 'pl')
        board.set_piece(4, 3, 'pl')  # own piece
        moves = get_valid_moves(board, GameContext(), 'pl', 5, 4)
        assert (4, 3) not in moves

    def test_pawn_at_edge_of_board(self):
        """Pawn on the a-file should not attempt to capture off the left edge."""
        board = empty_board()
        board.set_piece(5, 0, 'pl')
        moves = get_valid_moves(board, GameContext(), 'pl', 5, 0)
        # Should not crash from checking y=-1
        assert (4, 0) in moves

    def test_dark_pawn_capture_diagonal(self):
        """Dark pawn should be able to capture on both forward diagonals."""
        board = empty_board()
        board.set_piece(2, 4, 'pd')
        board.set_piece(3, 3, 'pl')
        board.set_piece(3, 5, 'pl')
        moves = get_valid_moves(board, GameContext(), 'pd', 2, 4)
        assert (3, 3) in moves
        assert (3, 5) in moves
