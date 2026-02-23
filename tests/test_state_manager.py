"""Tests for engine/game_engine.py"""
from pgchess.state_manager import StateManager


def setup_engine(pieces):
    """Create an engine with an empty board and place pieces.
    pieces: list of (x, y, piece_code) tuples
    """
    engine = StateManager()
    engine._state._board = [['' for _ in range(8)] for _ in range(8)]
    for x, y, code in pieces:
        engine._state.set_piece(x, y, code)
    return engine


class TestExecuteMove:
    def test_basic_move(self):
        engine = setup_engine([(6, 4, 'pl'), (7, 4, 'kl'), (0, 4, 'kd')])
        result = engine.execute_move('pl', 6, 4, 4, 4)
        assert engine.get_piece(4, 4) == 'pl'
        assert engine.get_piece(6, 4) == ''
        assert result['is_capture'] is False
        assert result['is_promotion'] is False

    def test_capture_detected(self):
        engine = setup_engine(
            [(4, 4, 'nl'), (3, 3, 'pd'), (7, 4, 'kl'), (0, 4, 'kd')])
        result = engine.execute_move('nl', 4, 4, 3, 3)
        assert result['is_capture'] is True

    def test_castling_rights_updated_on_king_move(self):
        engine = StateManager()
        engine._state.clear_square(6, 4)  # clear pawn in front of king
        engine.execute_move('kl', 7, 4, 6, 4)
        assert engine._context.has_king_moved('l') is True
        assert engine._context.has_king_moved('d') is False

    def test_castling_rights_updated_on_rook_move(self):
        engine = StateManager()
        engine._state.clear_square(6, 0)  # clear pawn in front of rook
        engine.execute_move('rl', 7, 0, 6, 0)
        assert engine._context.has_rook_moved('l', 0) is True
        assert engine._context.has_rook_moved('l', 7) is False

    def test_en_passant_target_set_on_double_pawn_move(self):
        engine = setup_engine([(6, 4, 'pl'), (7, 4, 'kl'), (0, 4, 'kd')])
        engine.execute_move('pl', 6, 4, 4, 4)
        assert engine._context.get_en_passant_target() == (5, 4)

    def test_en_passant_target_cleared_on_non_pawn_move(self):
        engine = setup_engine([(4, 4, 'nl'), (7, 4, 'kl'), (0, 4, 'kd')])
        engine._context.set_en_passant_target((5, 3))
        engine.execute_move('nl', 4, 4, 2, 3)
        assert engine._context.get_en_passant_target() is None


class TestPromotion:
    def test_promotion_detected(self):
        engine = setup_engine([(1, 3, 'pl'), (7, 4, 'kl'), (0, 4, 'kd')])
        result = engine.execute_move('pl', 1, 3, 0, 3)
        assert result['is_promotion'] is True
        assert result['promotion_square'] == (0, 3)

    def test_promote_pawn(self):
        engine = setup_engine([(0, 3, 'pl'), (7, 4, 'kl'), (0, 4, 'kd')])
        engine.promote_pawn(0, 3, 'q')
        assert engine.get_piece(0, 3) == 'ql'

    def test_no_promotion_for_non_back_rank(self):
        engine = setup_engine([(3, 3, 'pl'), (7, 4, 'kl'), (0, 4, 'kd')])
        result = engine.execute_move('pl', 3, 3, 2, 3)
        assert result['is_promotion'] is False


class TestCastlingExecution:
    def test_kingside_castle(self):
        engine = setup_engine([(7, 4, 'kl'), (7, 7, 'rl'), (0, 4, 'kd')])
        engine.execute_move('kl', 7, 4, 7, 6)
        assert engine.get_piece(7, 6) == 'kl'
        assert engine.get_piece(7, 5) == 'rl'
        assert engine.get_piece(7, 7) == ''

    def test_queenside_castle(self):
        engine = setup_engine([(7, 4, 'kl'), (7, 0, 'rl'), (0, 4, 'kd')])
        engine.execute_move('kl', 7, 4, 7, 2)
        assert engine.get_piece(7, 2) == 'kl'
        assert engine.get_piece(7, 3) == 'rl'
        assert engine.get_piece(7, 0) == ''


class TestEnPassantExecution:
    def test_en_passant_capture(self):
        engine = setup_engine(
            [(3, 4, 'pl'), (3, 3, 'pd'), (7, 4, 'kl'), (0, 4, 'kd')])
        engine._context.set_en_passant_target((2, 3))
        # remove pawn from board (simulating drag_start)
        engine._state.clear_square(3, 4)
        result = engine.execute_move('pl', 3, 4, 2, 3)
        assert engine.get_piece(2, 3) == 'pl'
        assert engine.get_piece(3, 3) == ''  # captured pawn removed
        assert result['is_capture'] is True


class TestGameStateChecks:
    def test_check_detection(self):
        engine = setup_engine([(7, 4, 'kl'), (0, 4, 'rd'), (0, 0, 'kd')])
        assert engine.is_in_check('l') is True
        assert engine.is_in_check('d') is False

    def test_checkmate_detection(self):
        # back rank mate
        engine = setup_engine(
            [(7, 0, 'kl'), (6, 0, 'pl'), (6, 1, 'pl'), (0, 7, 'rd'), (0, 0, 'kd')])
        engine.execute_move('rd', 0, 7, 7, 7)
        assert engine.is_in_checkmate('l') is True

    def test_stalemate_detection(self):
        engine = setup_engine([(0, 0, 'kl'), (2, 1, 'qd'), (7, 7, 'kd')])
        assert engine.is_in_stalemate('l') is True
        assert engine.is_in_checkmate('l') is False


class TestValidMoves:
    def test_get_valid_moves_with_context(self):
        """Castling should appear in valid moves when context allows it."""
        engine = setup_engine([(7, 4, 'kl'), (7, 7, 'rl'), (0, 4, 'kd')])
        engine._state.clear_square(7, 4)  # simulating drag_start
        moves = engine.get_valid_moves('kl', 7, 4)
        assert (7, 6) in moves  # kingside castle

    def test_get_valid_moves_no_castle_after_king_moved(self):
        engine = setup_engine([(7, 4, 'kl'), (7, 7, 'rl'), (0, 4, 'kd')])
        engine._context.mark_king_moved('l')
        engine._state.clear_square(7, 4)
        moves = engine.get_valid_moves('kl', 7, 4)
        assert (7, 6) not in moves
