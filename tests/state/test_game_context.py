"""Tests for engine/game_context.py"""
from pgchess.state.game_context import GameContext


class TestCastlingRights:
    """Tests for castling rights tracking in GameContext."""

    def test_king_not_moved_initially(self):
        """Neither king should be flagged as moved on a fresh context."""
        ctx = GameContext()
        assert ctx.has_king_moved('l') is False
        assert ctx.has_king_moved('d') is False

    def test_mark_king_moved(self):
        """Marking the light king as moved should only affect the light king flag."""
        ctx = GameContext()
        ctx.mark_king_moved('l')
        assert ctx.has_king_moved('l') is True
        assert ctx.has_king_moved('d') is False

    def test_rook_not_moved_initially(self):
        """Neither rook should be flagged as moved on a fresh context."""
        ctx = GameContext()
        assert ctx.has_rook_moved('l', 0) is False
        assert ctx.has_rook_moved('l', 7) is False

    def test_mark_rook_moved(self):
        """Marking one rook as moved should not affect the other rook's flag."""
        ctx = GameContext()
        ctx.mark_rook_moved('d', 7)
        assert ctx.has_rook_moved('d', 7) is True
        assert ctx.has_rook_moved('d', 0) is False


class TestEnPassant:
    """Tests for en passant target tracking in GameContext."""

    def test_no_target_initially(self):
        """A fresh context should have no en passant target."""
        ctx = GameContext()
        assert ctx.get_en_passant_target() is None

    def test_set_and_get_target(self):
        """Setting a target should make it retrievable via get_en_passant_target."""
        ctx = GameContext()
        ctx.set_en_passant_target((2, 3))
        assert ctx.get_en_passant_target() == (2, 3)

    def test_clear_target(self):
        """Setting target to None should clear any previously stored target."""
        ctx = GameContext()
        ctx.set_en_passant_target((2, 3))
        ctx.set_en_passant_target(None)
        assert ctx.get_en_passant_target() is None


class TestTurnManagement:
    """Tests for turn switching and color querying in GameContext."""

    def test_light_starts(self):
        """A fresh context should report it is light's turn."""
        ctx = GameContext()
        assert ctx.current_color() == 'l'

    def test_switch_turn(self):
        """switch_turn should alternate between light and dark each call."""
        ctx = GameContext()
        ctx.switch_turn()
        assert ctx.current_color() == 'd'
        ctx.switch_turn()
        assert ctx.current_color() == 'l'

    def test_is_turn(self):
        """is_turn should return True only for pieces matching the current player's color."""
        ctx = GameContext()
        assert ctx.is_turn('pl') is True
        assert ctx.is_turn('pd') is False
        ctx.switch_turn()
        assert ctx.is_turn('pl') is False
        assert ctx.is_turn('pd') is True
