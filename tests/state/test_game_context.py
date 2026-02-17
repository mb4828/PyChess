"""Tests for engine/game_context.py"""
from pychess.state.game_context import GameContext


class TestCastlingRights:
    def test_king_not_moved_initially(self):
        ctx = GameContext()
        assert ctx.has_king_moved('l') is False
        assert ctx.has_king_moved('d') is False

    def test_mark_king_moved(self):
        ctx = GameContext()
        ctx.mark_king_moved('l')
        assert ctx.has_king_moved('l') is True
        assert ctx.has_king_moved('d') is False

    def test_rook_not_moved_initially(self):
        ctx = GameContext()
        assert ctx.has_rook_moved('l', 0) is False
        assert ctx.has_rook_moved('l', 7) is False

    def test_mark_rook_moved(self):
        ctx = GameContext()
        ctx.mark_rook_moved('d', 7)
        assert ctx.has_rook_moved('d', 7) is True
        assert ctx.has_rook_moved('d', 0) is False


class TestEnPassant:
    def test_no_target_initially(self):
        ctx = GameContext()
        assert ctx.get_en_passant_target() is None

    def test_set_and_get_target(self):
        ctx = GameContext()
        ctx.set_en_passant_target((2, 3))
        assert ctx.get_en_passant_target() == (2, 3)

    def test_clear_target(self):
        ctx = GameContext()
        ctx.set_en_passant_target((2, 3))
        ctx.set_en_passant_target(None)
        assert ctx.get_en_passant_target() is None


class TestTurnManagement:
    def test_light_starts(self):
        ctx = GameContext()
        assert ctx.current_color() == 'l'
        assert ctx.is_light_turn is True

    def test_switch_turn(self):
        ctx = GameContext()
        ctx.switch_turn()
        assert ctx.current_color() == 'd'
        ctx.switch_turn()
        assert ctx.current_color() == 'l'

    def test_is_turn(self):
        ctx = GameContext()
        assert ctx.is_turn('pl') is True
        assert ctx.is_turn('pd') is False
        ctx.switch_turn()
        assert ctx.is_turn('pl') is False
        assert ctx.is_turn('pd') is True
