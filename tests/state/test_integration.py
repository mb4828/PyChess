"""Integration tests that simulate multi-move games to verify state consistency."""
from pychess.state.game_state import GameState
from pychess.state_manager import StateManager
from pychess.state.move_validator import is_in_check, is_in_checkmate, is_in_stalemate


def setup_engine(pieces):
    """Create an engine with an empty board and place pieces."""
    engine = StateManager()
    engine.get_state()._board = [['' for _ in range(8)] for _ in range(8)]
    for x, y, code in pieces:
        engine.get_state().set_piece(x, y, code)
    return engine


def simulate_drag_move(engine, piece, start_x, start_y, end_x, end_y):
    """Simulate a full drag-and-drop move: clear origin, get valid moves, execute, switch turn.

    Returns (result_dict, valid_moves_list).
    Asserts the destination is in the valid moves list.
    """
    engine.get_state().clear_square(start_x, start_y)
    valid_moves = engine.get_valid_moves(piece, start_x, start_y)
    assert (end_x, end_y) in valid_moves, (
        f"{piece} at ({start_x},{start_y}) cannot reach ({end_x},{end_y}). "
        f"Valid moves: {sorted(valid_moves)}"
    )
    result = engine.execute_move(piece, start_x, start_y, end_x, end_y)
    engine.switch_turn()
    return result, valid_moves


def get_drag_valid_moves(engine, x, y):
    """Simulate picking up a piece and getting its valid moves, then put it back."""
    piece = engine.get_piece(x, y)
    assert piece, f"No piece at ({x},{y})"
    engine.get_state().clear_square(x, y)
    moves = engine.get_valid_moves(piece, x, y)
    engine.get_state().set_piece(x, y, piece)
    return moves


class TestMultiMoveGame:
    """Play through a real opening (Ruy Lopez) and verify moves at each step."""

    def test_ruy_lopez_opening(self):
        engine = StateManager()

        # 1. e4
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        assert engine.get_piece(4, 4) == 'pl'
        assert engine.get_piece(6, 4) == ''

        # 1... e5
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)
        assert engine.get_piece(3, 4) == 'pd'

        # 2. Nf3
        simulate_drag_move(engine, 'nl', 7, 6, 5, 5)
        assert engine.get_piece(5, 5) == 'nl'

        # 2... Nc6
        simulate_drag_move(engine, 'nd', 0, 1, 2, 2)
        assert engine.get_piece(2, 2) == 'nd'

        # 3. Bb5
        simulate_drag_move(engine, 'bl', 7, 5, 3, 1)
        assert engine.get_piece(3, 1) == 'bl'

        # 3... a6 (threatening the bishop)
        simulate_drag_move(engine, 'pd', 1, 0, 2, 0)

        # Verify bishop on b5 has full diagonal range + captures
        bishop_moves = get_drag_valid_moves(engine, 3, 1)
        assert (2, 0) in bishop_moves, "Bishop should be able to capture pawn on a6"
        assert (2, 2) in bishop_moves, "Bishop should be able to capture knight on c6"
        assert (4, 2) in bishop_moves, "Bishop should reach c4"
        assert (4, 0) in bishop_moves, "Bishop should reach a4"

        # Verify knight on f3 still has moves
        knight_moves = get_drag_valid_moves(engine, 5, 5)
        assert len(knight_moves) > 0, "Knight on f3 should have valid moves"
        assert (3, 4) in knight_moves or (4, 3) in knight_moves, (
            "Knight should be able to reach d4 or e5 area"
        )

    def test_italian_game_with_captures(self):
        """Play through Italian Game with captures to test state consistency."""
        engine = StateManager()

        # 1. e4 e5
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)

        # 2. Nf3 Nc6
        simulate_drag_move(engine, 'nl', 7, 6, 5, 5)
        simulate_drag_move(engine, 'nd', 0, 1, 2, 2)

        # 3. Bc4 Bc5
        simulate_drag_move(engine, 'bl', 7, 5, 4, 2)
        simulate_drag_move(engine, 'bd', 0, 5, 3, 2)

        # 4. d3 d6
        simulate_drag_move(engine, 'pl', 6, 3, 5, 3)
        simulate_drag_move(engine, 'pd', 1, 3, 2, 3)

        # Verify pieces haven't been lost/duplicated
        assert engine.get_piece(
            4, 2) == 'bl', "Light bishop should still be on c4"
        assert engine.get_piece(
            3, 2) == 'bd', "Dark bishop should still be on c5"
        assert engine.get_piece(
            5, 5) == 'nl', "Light knight should still be on f3"
        assert engine.get_piece(
            2, 2) == 'nd', "Dark knight should still be on c6"

        # Light pawn on d3 (5,3) should be able to advance to d4 (4,3) which is empty
        d3_pawn_moves = get_drag_valid_moves(engine, 5, 3)
        assert (
            4, 3) in d3_pawn_moves, "d3 pawn should be able to advance to d4 (empty square)"
        # d3 pawn should NOT be able to capture diagonally (no enemies on c4 or e4)
        # c4 (4,2) has the light bishop, e4 (4,4) has the light pawn
        assert (4, 2) not in d3_pawn_moves, "d3 pawn can't capture own bishop on c4"

        # Dark pawn on d6 (2,3) should be able to advance to d5 (3,3) which is empty
        d6_pawn_moves = get_drag_valid_moves(engine, 2, 3)
        assert (3, 3) in d6_pawn_moves, "d6 pawn should be able to advance to d5"


class TestPawnCapturesAfterMultipleMoves:
    """Specifically test that pawn captures work correctly after several moves."""

    def test_pawn_capture_available_midgame(self):
        engine = StateManager()

        # 1. e4 d5 (Scandinavian Defense)
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 3, 3, 3)

        # Light pawn on e4 should be able to capture dark pawn on d5
        e4_moves = get_drag_valid_moves(engine, 4, 4)
        assert (3, 3) in e4_moves, "e4 pawn must be able to capture d5 pawn"
        assert (3, 4) in e4_moves, "e4 pawn should be able to advance to e5"

        # 2. exd5
        simulate_drag_move(engine, 'pl', 4, 4, 3, 3)
        assert engine.get_piece(
            3, 3) == 'pl', "Light pawn should be on d5 after capture"
        assert engine.get_piece(
            4, 4) == '', "e4 should be empty after pawn moved"

    def test_pawn_capture_both_diagonals(self):
        """Set up a position where a pawn can capture on both diagonals."""
        engine = setup_engine([
            (7, 4, 'kl'), (0, 4, 'kd'),
            (4, 3, 'pl'),  # light pawn on d4
            (3, 2, 'pd'),  # dark pawn on c5 (capturable)
            (3, 4, 'pd'),  # dark pawn on e5 (capturable)
        ])

        pawn_moves = get_drag_valid_moves(engine, 4, 3)
        assert (3, 3) in pawn_moves, "Pawn should be able to advance to d5"
        assert (3, 2) in pawn_moves, "Pawn should be able to capture on c5"
        assert (3, 4) in pawn_moves, "Pawn should be able to capture on e5"

    def test_dark_pawn_capture_after_several_moves(self):
        engine = StateManager()

        # 1. e4 e5 2. d4
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)
        simulate_drag_move(engine, 'pl', 6, 3, 4, 3)

        # Dark pawn on e5 should be able to capture d4
        e5_moves = get_drag_valid_moves(engine, 3, 4)
        assert (4, 3) in e5_moves, "e5 pawn must be able to capture d4 pawn"


class TestBishopSlidingAfterMultipleMoves:
    """Verify bishops maintain full diagonal range throughout the game."""

    def test_bishop_full_diagonal_midgame(self):
        engine = StateManager()

        # 1. e4 e5 2. Bc4
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)
        simulate_drag_move(engine, 'bl', 7, 5, 4, 2)

        # 2... Nf6
        simulate_drag_move(engine, 'nd', 0, 6, 2, 5)

        # Bishop on c4 should have full diagonal range
        bishop_moves = get_drag_valid_moves(engine, 4, 2)

        # Diagonal toward a6: (3, 1), (2, 0) - but (3,1) should be reachable
        assert (3, 1) in bishop_moves, "Bishop c4 should reach b5"
        assert (2, 0) in bishop_moves, "Bishop c4 should reach a6"

        # Diagonal toward f7: (3, 3), (2, 4) should be blocked by dark pawn on e5? No, (2,4) is not diagonal from c4
        # Actually (3,3) = d5, (2,4) = e6... wait let me think about diagonals from c4 (4,2)
        # Up-right: (3,3), (2,4), (1,5), (0,6) - (1,5) has dark pawn f7 initially
        assert (3, 3) in bishop_moves, "Bishop c4 should reach d5"

        # Down-left: (5,1), (6,0) - (6,0) has light pawn
        assert (5, 1) in bishop_moves, "Bishop c4 should reach b3"

        # Down-right: (5,3) - blocked by light pawn on d3? No, d3 pawn hasn't moved
        # (5,3) has a pawn on d2 at (6,3)... actually (5,3) is d3, which is empty
        assert (5, 3) in bishop_moves, "Bishop c4 should reach d3"

    def test_bishop_not_limited_to_one_square(self):
        """Regression: bishop should slide along full diagonal, not stop after 1 square."""
        engine = setup_engine([
            (7, 4, 'kl'), (0, 4, 'kd'),
            (4, 4, 'bl'),  # bishop on e4
        ])

        bishop_moves = get_drag_valid_moves(engine, 4, 4)

        # Should have moves along all 4 diagonals until edge of board
        # Up-right: (3,5), (2,6), (1,7)
        assert (3, 5) in bishop_moves
        assert (2, 6) in bishop_moves
        assert (1, 7) in bishop_moves

        # Up-left: (3,3), (2,2), (1,1), (0,0)
        assert (3, 3) in bishop_moves
        assert (2, 2) in bishop_moves
        assert (1, 1) in bishop_moves
        assert (0, 0) in bishop_moves

        # Down-right: (5,5), (6,6), (7,7)
        assert (5, 5) in bishop_moves
        assert (6, 6) in bishop_moves
        assert (7, 7) in bishop_moves

        # Down-left: (5,3), (6,2), (7,1)
        assert (5, 3) in bishop_moves
        assert (6, 2) in bishop_moves
        assert (7, 1) in bishop_moves

        assert len(
            bishop_moves) == 13, f"Bishop on e4 (empty board + 2 kings) should have 13 moves, got {len(bishop_moves)}"


class TestKnightMovesAfterMultipleMoves:
    """Verify knights have correct moves after several game turns."""

    def test_knight_moves_midgame(self):
        engine = StateManager()

        # 1. e4 e5 2. Nf3 Nc6 3. d4
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)
        simulate_drag_move(engine, 'nl', 7, 6, 5, 5)
        simulate_drag_move(engine, 'nd', 0, 1, 2, 2)
        simulate_drag_move(engine, 'pl', 6, 3, 4, 3)

        # Dark knight on c6 should have multiple moves
        knight_moves = get_drag_valid_moves(engine, 2, 2)
        assert len(knight_moves) > 0, "Knight on c6 must have valid moves"

        # Knight can go to: a5(4,0)? No that's wrong coord. Let me think:
        # Knight at (2,2) = c6. L-shape moves:
        # (0,1)=b8 has nothing (knight moved from there), (0,3)=d8 has queen
        # (1,0)=a7 has pawn, (1,4)=e7 has nothing (pawn moved)
        # (3,0)=a5, (3,4)=e5 has pawn
        # (4,1)=b4, (4,3)=d4 has pawn
        # Filter: same color blocks, check-safety
        assert (3, 0) in knight_moves, "Knight c6 should be able to go to a5"
        # (4, 3) has a light pawn - knight can capture it
        assert (4, 3) in knight_moves, "Knight c6 should be able to capture d4 pawn"

    def test_knight_not_blocked_on_open_board(self):
        """Regression: knight should have all 8 L-shape moves from center of empty board."""
        engine = setup_engine([
            (7, 4, 'kl'), (0, 4, 'kd'),
            (4, 4, 'nl'),  # knight on e4
        ])

        knight_moves = get_drag_valid_moves(engine, 4, 4)
        expected = {(2, 3), (2, 5), (3, 2), (3, 6),
                    (5, 2), (5, 6), (6, 3), (6, 5)}
        assert set(knight_moves) == expected, (
            f"Knight on e4 should have 8 moves, got {sorted(knight_moves)}"
        )


class TestCheckmateDetectionAfterMultipleMoves:
    """Verify checkmate is correctly detected after a sequence of moves."""

    def test_scholars_mate(self):
        """Scholar's mate: 1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6?? 4. Qxf7#"""
        engine = StateManager()

        # 1. e4 e5
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)

        # 2. Bc4 Nc6
        simulate_drag_move(engine, 'bl', 7, 5, 4, 2)
        simulate_drag_move(engine, 'nd', 0, 1, 2, 2)

        # 3. Qh5 Nf6??
        simulate_drag_move(engine, 'ql', 7, 3, 3, 7)
        simulate_drag_move(engine, 'nd', 0, 6, 2, 5)

        # 4. Qxf7# (queen captures f7 pawn - checkmate)
        result, _ = simulate_drag_move(engine, 'ql', 3, 7, 1, 5)
        assert result['is_capture'] is True

        # Now it's dark's turn - should be checkmate
        assert is_in_check(engine.get_state(),
                           'd') is True, "Dark king should be in check"
        assert is_in_checkmate(
            engine.get_state(), 'd') is True, "This should be checkmate"
        assert not is_in_stalemate(
            engine.get_state(), 'd'), "This is not stalemate"

    def test_fools_mate(self):
        """Fool's mate: 1. f3 e5 2. g4?? Qh4#"""
        engine = StateManager()

        # 1. f3 e5
        simulate_drag_move(engine, 'pl', 6, 5, 5, 5)
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)

        # 2. g4 Qh4#
        simulate_drag_move(engine, 'pl', 6, 6, 4, 6)
        simulate_drag_move(engine, 'qd', 0, 3, 4, 7)

        # Light should be in checkmate
        assert is_in_check(engine.get_state(),
                           'l') is True, "Light king should be in check"
        assert is_in_checkmate(
            engine.get_state(), 'l') is True, "This should be checkmate"

    def test_back_rank_mate_after_sequence(self):
        """Set up a back rank mate position: rook delivers mate along the back rank."""
        engine = setup_engine([
            (7, 6, 'kl'), (6, 5, 'pl'), (6, 6, 'pl'), (6,
                                                       7, 'pl'),  # castled king position
            (0, 0, 'kd'), (7, 0, 'rd'),  # dark rook already on a1 (back rank)
        ])
        # Dark's turn — rook is already on the back rank, light king is trapped
        engine.get_context()._is_light_turn = False

        # Verify the position: light king on g1 hemmed in by own pawns on f2/g2/h2
        # Dark rook on a1 controls the entire 1st rank
        assert is_in_check(
            engine.get_state(), 'l') is True, "Light king should be in check from rook on a1"
        assert is_in_checkmate(
            engine.get_state(), 'l') is True, "This should be back rank checkmate"


class TestBoardStateConsistency:
    """Verify the board state doesn't get corrupted across moves."""

    def test_piece_count_preserved(self):
        """After several moves without captures, piece count should be constant."""
        engine = StateManager()

        def count_pieces():
            count = 0
            for row in engine.get_state()._board:
                for cell in row:
                    if cell:
                        count += 1
            return count

        initial_count = count_pieces()
        assert initial_count == 32

        # 1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 (no captures)
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        assert count_pieces() == 32
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)
        assert count_pieces() == 32
        simulate_drag_move(engine, 'nl', 7, 6, 5, 5)
        assert count_pieces() == 32
        simulate_drag_move(engine, 'nd', 0, 1, 2, 2)
        assert count_pieces() == 32
        simulate_drag_move(engine, 'bl', 7, 5, 4, 2)
        assert count_pieces() == 32
        simulate_drag_move(engine, 'bd', 0, 5, 3, 2)
        assert count_pieces() == 32

    def test_piece_count_after_capture(self):
        """After a capture, piece count should decrease by 1."""
        engine = StateManager()

        # 1. e4 d5 2. exd5 (capture)
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 3, 3, 3)
        result, _ = simulate_drag_move(engine, 'pl', 4, 4, 3, 3)
        assert result['is_capture'] is True

        count = sum(1 for row in engine.get_state()._board for cell in row if cell)
        assert count == 31, f"After 1 capture, should have 31 pieces, got {count}"

    def test_no_ghost_pieces_after_castling(self):
        """After castling, no duplicate king or rook should exist."""
        engine = setup_engine([
            (7, 4, 'kl'), (7, 7, 'rl'), (0, 4, 'kd'),
        ])

        simulate_drag_move(engine, 'kl', 7, 4, 7, 6)

        # Verify: king on g1, rook on f1, old squares empty
        assert engine.get_piece(7, 6) == 'kl'
        assert engine.get_piece(7, 5) == 'rl'
        assert engine.get_piece(7, 4) == ''
        assert engine.get_piece(7, 7) == ''

        # Count kings and rooks
        kings = sum(
            1 for row in engine.get_state()._board for c in row if c.startswith('k') if c)
        rooks = sum(
            1 for row in engine.get_state()._board for c in row if c.startswith('r') if c)
        assert kings == 2, f"Should have exactly 2 kings, got {kings}"

    def test_checkmate_stalemate_dont_corrupt_board(self):
        """Calling is_in_checkmate/stalemate should not mutate the board."""
        engine = StateManager()

        # Play a few moves
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)
        simulate_drag_move(engine, 'nl', 7, 6, 5, 5)

        # Snapshot the board
        import copy
        board_before = copy.deepcopy(engine.get_state()._board)

        # Call checkmate and stalemate detection (these iterate the board)
        is_in_checkmate(engine.get_state(), 'd')
        is_in_stalemate(engine.get_state(), 'd')
        is_in_check(engine.get_state(), 'd')

        # Board should be unchanged
        assert engine.get_state()._board == board_before, "Check/checkmate/stalemate detection mutated the board!"

    def test_valid_moves_dont_corrupt_board(self):
        """Getting valid moves for a piece should not mutate the board."""
        engine = StateManager()

        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 4, 3, 4)

        import copy
        board_before = copy.deepcopy(engine.get_state()._board)

        # Get valid moves for several pieces (simulating drag_start behavior)
        for x in range(8):
            for y in range(8):
                piece = engine.get_piece(x, y)
                if piece:
                    engine.get_state().clear_square(x, y)
                    engine.get_valid_moves(piece, x, y)
                    engine.get_state().set_piece(x, y, piece)

        assert engine.get_state()._board == board_before, "Getting valid moves mutated the board!"


class TestEnPassantMultiMove:
    """Verify en passant works correctly in a real game sequence."""

    def test_en_passant_available_after_double_push(self):
        engine = StateManager()

        # 1. e4 d5 2. e5 f5 (dark double-pushes f pawn next to white e5 pawn)
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'pd', 1, 3, 3, 3)
        # not a capture since exd5 was played? Wait...
        simulate_drag_move(engine, 'pl', 4, 4, 3, 4)

        # Actually let me redo this. 1. e4 Nf6 2. e5 d5 (en passant available)
        engine = StateManager()
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'nd', 0, 6, 2, 5)
        simulate_drag_move(engine, 'pl', 4, 4, 3, 4)  # e5
        # d5 - double push next to e5 pawn
        simulate_drag_move(engine, 'pd', 1, 3, 3, 3)

        # En passant target should be set
        assert engine.get_context().get_en_passant_target() == (2, 3)

        # Light pawn on e5 (3,4) should be able to capture en passant on d6 (2,3)
        e5_moves = get_drag_valid_moves(engine, 3, 4)
        assert (2, 3) in e5_moves, "En passant capture should be available"
        assert (2, 4) in e5_moves, "Normal advance should also be available"

    def test_en_passant_expires_after_one_move(self):
        engine = StateManager()

        # 1. e4 Nf6 2. e5 d5 3. Nf3 (white doesn't take en passant)
        simulate_drag_move(engine, 'pl', 6, 4, 4, 4)
        simulate_drag_move(engine, 'nd', 0, 6, 2, 5)
        simulate_drag_move(engine, 'pl', 4, 4, 3, 4)
        simulate_drag_move(engine, 'pd', 1, 3, 3, 3)

        # En passant is available now
        assert engine.get_context().get_en_passant_target() == (2, 3)

        # White plays something else
        simulate_drag_move(engine, 'nl', 7, 6, 5, 5)

        # En passant should no longer be available
        assert engine.get_context().get_en_passant_target() is None
