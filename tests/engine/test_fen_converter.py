"""Tests for pgchess.engine.engine.FENConverter."""
import pytest

from pgchess.engine.engine import FENConverter
from pgchess.state.game_context import GameContext
from pgchess.state.game_state import GameState


class TestToFen:
    def test_starting_position_piece_placement(self):
        """Starting position should produce the standard FEN piece placement string."""
        state = GameState()
        context = GameContext()
        fen = FENConverter.to_fen(state, context)
        assert fen.split()[0] == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'

    def test_active_color_white_at_start(self):
        """White to move should produce 'w' in the active color field."""
        state = GameState()
        context = GameContext()
        fen = FENConverter.to_fen(state, context)
        assert fen.split()[1] == 'w'

    def test_active_color_black_after_switch(self):
        """After one turn switch, active color field should be 'b'."""
        state = GameState()
        context = GameContext()
        context.switch_turn()
        fen = FENConverter.to_fen(state, context)
        assert fen.split()[1] == 'b'

    def test_castling_all_rights_at_start(self):
        """Starting position should contain all four castling rights."""
        state = GameState()
        context = GameContext()
        castling = FENConverter.to_fen(state, context).split()[2]
        assert 'K' in castling
        assert 'Q' in castling
        assert 'k' in castling
        assert 'q' in castling

    def test_castling_none_when_all_kings_moved(self):
        """When both kings have moved, castling field should be '-'."""
        state = GameState()
        context = GameContext()
        context.mark_king_moved('l')
        context.mark_king_moved('d')
        castling = FENConverter.to_fen(state, context).split()[2]
        assert castling == '-'

    def test_castling_white_kingside_only(self):
        """Only white kingside right available should produce 'K' only."""
        state = GameState()
        context = GameContext()
        context.mark_king_moved('d')     # black king moved → no black rights
        context.mark_rook_moved('l', 0)  # white queenside rook moved
        castling = FENConverter.to_fen(state, context).split()[2]
        assert castling == 'K'

    def test_en_passant_none(self):
        """No en passant target should produce '-'."""
        state = GameState()
        context = GameContext()
        assert FENConverter.to_fen(state, context).split()[3] == '-'

    def test_en_passant_e3(self):
        """En passant target at e3 (row=5, col=4) should produce 'e3'."""
        state = GameState()
        context = GameContext()
        context.set_en_passant_target((5, 4))
        assert FENConverter.to_fen(state, context).split()[3] == 'e3'

    def test_en_passant_a6(self):
        """En passant target at a6 (row=2, col=0) should produce 'a6'."""
        state = GameState()
        context = GameContext()
        context.set_en_passant_target((2, 0))
        assert FENConverter.to_fen(state, context).split()[3] == 'a6'

    def test_empty_board_piece_placement(self):
        """Empty board should produce '8/8/8/8/8/8/8/8'."""
        state = GameState.empty()
        context = GameContext()
        assert FENConverter.to_fen(state, context).split()[0] == '8/8/8/8/8/8/8/8'

    def test_single_king_on_e1(self):
        """A lone white king on e1 (row=7, col=4) should produce '8/8/8/8/8/8/8/4K3'."""
        state = GameState.empty()
        context = GameContext()
        state.set_piece(7, 4, 'kl')
        placement = FENConverter.to_fen(state, context).split()[0]
        assert placement == '8/8/8/8/8/8/8/4K3'

    def test_fen_has_six_fields(self):
        """FEN string should always have exactly six space-separated fields."""
        state = GameState()
        context = GameContext()
        parts = FENConverter.to_fen(state, context).split()
        assert len(parts) == 6


class TestFromLan:
    def test_e2e4(self):
        """'e2e4' → white pawn advance: (start_row=6, start_col=4, end_row=4, end_col=4, promo='')."""
        assert FENConverter.from_lan('e2e4') == (6, 4, 4, 4, '')

    def test_e7e5(self):
        """'e7e5' → black pawn advance: (1, 4, 3, 4, '')."""
        assert FENConverter.from_lan('e7e5') == (1, 4, 3, 4, '')

    def test_promotion_queen(self):
        """'e7e8q' should return promotion character 'q'."""
        assert FENConverter.from_lan('e7e8q') == (1, 4, 0, 4, 'q')

    def test_promotion_knight(self):
        """'g7g8n' should return promotion character 'n'."""
        assert FENConverter.from_lan('g7g8n') == (1, 6, 0, 6, 'n')

    def test_a_file_maps_to_col_zero(self):
        """'a1a8' should map the a-file to column index 0."""
        start_row, start_col, end_row, end_col, _ = FENConverter.from_lan('a1a8')
        assert start_col == 0
        assert end_col == 0

    def test_h_file_maps_to_col_seven(self):
        """'h1h8' should map the h-file to column index 7."""
        _, start_col, _, end_col, _ = FENConverter.from_lan('h1h8')
        assert start_col == 7
        assert end_col == 7

    def test_rank_1_maps_to_row_7(self):
        """Rank 1 (bottom of board) should map to row index 7."""
        start_row, _, _, _, _ = FENConverter.from_lan('a1a2')
        assert start_row == 7

    def test_rank_8_maps_to_row_zero(self):
        """Rank 8 (top of board) should map to row index 0."""
        _, _, end_row, _, _ = FENConverter.from_lan('a1a8')
        assert end_row == 0

    def test_no_promotion_for_four_char_lan(self):
        """Four-character LAN should produce an empty promotion string."""
        _, _, _, _, promo = FENConverter.from_lan('d2d4')
        assert promo == ''

    @pytest.mark.parametrize('lan,expected', [
        ('a2a4', (6, 0, 4, 0, '')),
        ('h7h8q', (1, 7, 0, 7, 'q')),
        ('d1d8', (7, 3, 0, 3, '')),
    ])
    def test_various_squares(self, lan, expected):
        """Parameterised spot-checks for diverse LAN inputs."""
        assert FENConverter.from_lan(lan) == expected
