"""Tests for pgchess.engine.sunfish_adapter.SunfishAdapter."""
import pytest

from pgchess.engine import sunfish
from pgchess.engine.sunfish_adapter import SunfishAdapter
from pgchess.state.game_context import GameContext
from pgchess.state.game_state import GameState


@pytest.fixture
def adapter():
    """Provide a SunfishAdapter instance."""
    return SunfishAdapter()


class TestBuildBoardString:
    def test_length_is_120(self, adapter):
        """Board string must be exactly 120 characters (10 chars × 12 rows in sunfish format)."""
        result = adapter._build_board_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        assert len(result) == 120

    def test_contains_black_back_rank(self, adapter):
        """Board string should contain the black back rank as a space-prefixed row."""
        result = adapter._build_board_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        assert ' rnbqkbnr\n' in result

    def test_contains_white_back_rank(self, adapter):
        """Board string should contain the white back rank as a space-prefixed row."""
        result = adapter._build_board_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        assert ' RNBQKBNR\n' in result

    def test_empty_rank_becomes_eight_dots(self, adapter):
        """An empty rank ('8') should expand to eight dots in the board string."""
        result = adapter._build_board_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        assert ' ........\n' in result

    def test_single_piece_on_otherwise_empty_board(self, adapter):
        """A lone king on e1 (4K3 in the last rank) should appear in the board string."""
        result = adapter._build_board_string('8/8/8/8/8/8/8/4K3')
        assert ' ....K...\n' in result


class TestParseCastling:
    def test_full_rights_not_rotated(self, adapter):
        """'KQkq', not rotated → white's wc=(True,True), bc=(True,True)."""
        wc, bc = adapter._parse_castling('KQkq', was_rotated=False)
        # wc: ('Q' in s, 'K' in s); bc: ('k' in s, 'q' in s)
        assert wc == (True, True)
        assert bc == (True, True)

    def test_full_rights_rotated(self, adapter):
        """'KQkq', rotated → wc=(True,True), bc=(True,True)."""
        wc, bc = adapter._parse_castling('KQkq', was_rotated=True)
        # wc: ('k' in s, 'q' in s); bc: ('Q' in s, 'K' in s)
        assert wc == (True, True)
        assert bc == (True, True)

    def test_no_rights_not_rotated(self, adapter):
        """'-' castling string should yield all False."""
        wc, bc = adapter._parse_castling('-', was_rotated=False)
        assert wc == (False, False)
        assert bc == (False, False)

    def test_white_kingside_only_not_rotated(self, adapter):
        """'K' only, not rotated → wc=(False, True), bc=(False, False)."""
        wc, bc = adapter._parse_castling('K', was_rotated=False)
        assert wc == (False, True)
        assert bc == (False, False)

    def test_black_queenside_only_rotated(self, adapter):
        """'q' only, rotated → wc=(False, True), bc=(False, False)."""
        wc, bc = adapter._parse_castling('q', was_rotated=True)
        # wc: ('k' in 'q'=False, 'q' in 'q'=True)
        assert wc == (False, True)
        assert bc == (False, False)

    def test_black_rights_only_not_rotated(self, adapter):
        """'kq' only, not rotated → wc=(False,False), bc=(True,True)."""
        wc, bc = adapter._parse_castling('kq', was_rotated=False)
        assert wc == (False, False)
        assert bc == (True, True)


class TestParseEp:
    def test_dash_not_rotated_returns_zero(self, adapter):
        """'-' en passant field should return 0 (no en passant)."""
        assert adapter._parse_ep('-', was_rotated=False) == 0

    def test_dash_rotated_returns_zero(self, adapter):
        """'-' en passant field, rotated, should also return 0."""
        assert adapter._parse_ep('-', was_rotated=True) == 0

    def test_e3_not_rotated(self, adapter):
        """'e3' not rotated should equal sunfish.parse('e3')."""
        assert adapter._parse_ep('e3', was_rotated=False) == sunfish.parse('e3')

    def test_e6_rotated(self, adapter):
        """'e6' rotated should equal 119 - sunfish.parse('e6')."""
        assert adapter._parse_ep('e6', was_rotated=True) == 119 - sunfish.parse('e6')

    def test_a3_not_rotated(self, adapter):
        """'a3' not rotated should equal sunfish.parse('a3')."""
        assert adapter._parse_ep('a3', was_rotated=False) == sunfish.parse('a3')


class TestMoveToLan:
    def test_e2e4_not_rotated(self, adapter):
        """Move from e2 to e4 without rotation should produce 'e2e4'."""
        move = sunfish.Move(sunfish.parse('e2'), sunfish.parse('e4'), '')
        assert adapter._move_to_lan(move, was_rotated=False) == 'e2e4'

    def test_e7e5_rotated(self, adapter):
        """Rotated move representing e7→e5 should un-rotate to 'e7e5'."""
        i = 119 - sunfish.parse('e7')
        j = 119 - sunfish.parse('e5')
        move = sunfish.Move(i, j, '')
        assert adapter._move_to_lan(move, was_rotated=True) == 'e7e5'

    def test_promotion_lowercased(self, adapter):
        """Promotion character should be lowercased in the LAN string."""
        move = sunfish.Move(sunfish.parse('e7'), sunfish.parse('e8'), 'Q')
        result = adapter._move_to_lan(move, was_rotated=False)
        assert result == 'e7e8q'

    def test_h1h8_not_rotated(self, adapter):
        """Move from h1 to h8 without rotation should produce 'h1h8'."""
        move = sunfish.Move(sunfish.parse('h1'), sunfish.parse('h8'), '')
        assert adapter._move_to_lan(move, was_rotated=False) == 'h1h8'


class TestGetBestMove:
    def test_returns_five_tuple(self, adapter):
        """get_best_move should always return a 5-element tuple."""
        state = GameState()
        context = GameContext()
        context.switch_turn()  # Black (computer) to move
        result = adapter.get_best_move(state, context, move_time_seconds=0.1)
        assert len(result) == 5

    def test_returns_valid_board_coordinates(self, adapter):
        """Returned coordinates should be within the 8×8 board."""
        state = GameState()
        context = GameContext()
        context.switch_turn()  # Black to move
        start_row, start_col, end_row, end_col, _ = adapter.get_best_move(
            state, context, move_time_seconds=0.1
        )
        assert 0 <= start_row <= 7
        assert 0 <= start_col <= 7
        assert 0 <= end_row <= 7
        assert 0 <= end_col <= 7

    def test_source_square_has_black_piece(self, adapter):
        """The source square of the returned move should hold a black piece."""
        state = GameState()
        context = GameContext()
        context.switch_turn()  # Black to move
        start_row, start_col, _, _, _ = adapter.get_best_move(
            state, context, move_time_seconds=0.1
        )
        piece = state.get_piece(start_row, start_col)
        assert piece.endswith('d'), f"Expected black piece at ({start_row}, {start_col}), got {piece!r}"

    def test_promotion_string_is_empty_or_single_char(self, adapter):
        """Promotion field should be either empty or a single lowercase character."""
        state = GameState()
        context = GameContext()
        context.switch_turn()
        _, _, _, _, promo = adapter.get_best_move(state, context, move_time_seconds=0.1)
        assert promo == '' or (len(promo) == 1 and promo.islower())
