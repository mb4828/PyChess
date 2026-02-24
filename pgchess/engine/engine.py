"""Abstract engine adapter interface and FEN/LAN converter utilities."""
import logging
from abc import ABC, abstractmethod
from typing import Tuple

from pgchess.state.game_context import GameContext
from pgchess.state.game_state import GameState

logger = logging.getLogger(__name__)

# Mapping from PGChess two-character piece codes to single FEN characters
_PIECE_TO_FEN = {
    'kl': 'K', 'ql': 'Q', 'rl': 'R', 'bl': 'B', 'nl': 'N', 'pl': 'P',
    'kd': 'k', 'qd': 'q', 'rd': 'r', 'bd': 'b', 'nd': 'n', 'pd': 'p',
}


class EngineAdapter(ABC):
    """Abstract interface for chess engine adapters.

    Implementations receive PGChess game state directly and return a move
    as PGChess board coordinates.  Each adapter owns its own protocol details
    (FEN conversion, subprocess management, etc.) internally.
    """

    @abstractmethod
    def get_best_move(
        self,
        state: GameState,
        context: GameContext,
        move_time_seconds: float = 1.0,
    ) -> Tuple[int, int, int, int, str]:
        """Return the best move for the current position.

        :param state: Current board state
        :param context: Current game context (castling rights, en passant, turn)
        :param move_time_seconds: Maximum time (in seconds) to spend searching
        :return: Tuple of ``(start_row, start_col, end_row, end_col, promotion)``
        """


class FENConverter:
    """Converts PGChess board/context state to FEN and LAN moves to board coordinates."""

    @staticmethod
    def to_fen(state: GameState, context: GameContext) -> str:
        """Build a FEN string from a PGChess game state and context.

        :param state: Current board state
        :param context: Current game context (castling rights, en passant, turn)
        :return: FEN string representing the position
        """
        piece_placement = FENConverter._build_piece_placement(state)
        active_color = 'w' if context.current_color() == 'l' else 'b'
        castling = FENConverter._build_castling(context)
        en_passant = FENConverter._build_en_passant(context)
        return f"{piece_placement} {active_color} {castling} {en_passant} 0 1"

    @staticmethod
    def from_lan(lan: str) -> Tuple[int, int, int, int, str]:
        """Convert a Long Algebraic Notation move string to PGChess board coordinates.

        :param lan: LAN move string, e.g. ``'e2e4'`` or ``'e7e8q'``
        :return: Tuple of ``(start_row, start_col, end_row, end_col, promotion)``
        """
        start_col = ord(lan[0]) - ord('a')
        start_row = 8 - int(lan[1])
        end_col = ord(lan[2]) - ord('a')
        end_row = 8 - int(lan[3])
        promotion = lan[4].lower() if len(lan) > 4 else ''
        logger.debug("from_lan %s → (%d,%d)→(%d,%d) prom=%r", lan, start_row, start_col, end_row, end_col, promotion)
        return start_row, start_col, end_row, end_col, promotion

    @staticmethod
    def _build_piece_placement(state: GameState) -> str:
        """Build the piece placement field of a FEN string (ranks 8 down to 1).

        :param state: Current board state
        :return: FEN piece placement string, e.g. ``'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'``
        """
        ranks = []
        for row in range(8):
            rank_str = ''
            empty = 0
            for col in range(8):
                piece_code = state.get_piece(row, col)
                if piece_code:
                    if empty:
                        rank_str += str(empty)
                        empty = 0
                    rank_str += _PIECE_TO_FEN.get(piece_code, '?')
                else:
                    empty += 1
            if empty:
                rank_str += str(empty)
            ranks.append(rank_str)
        return '/'.join(ranks)

    @staticmethod
    def _build_castling(context: GameContext) -> str:
        """Build the castling availability field of a FEN string.

        :param context: Current game context
        :return: Castling string, e.g. ``'KQkq'``, or ``'-'`` if none available
        """
        castling = ''
        if not context.has_king_moved('l'):
            if not context.has_rook_moved('l', 7):
                castling += 'K'  # White kingside (h-file rook, col 7)
            if not context.has_rook_moved('l', 0):
                castling += 'Q'  # White queenside (a-file rook, col 0)
        if not context.has_king_moved('d'):
            if not context.has_rook_moved('d', 7):
                castling += 'k'  # Black kingside
            if not context.has_rook_moved('d', 0):
                castling += 'q'  # Black queenside
        return castling or '-'

    @staticmethod
    def _build_en_passant(context: GameContext) -> str:
        """Build the en passant target square field of a FEN string.

        :param context: Current game context
        :return: Algebraic square string (e.g. ``'e3'``) or ``'-'``
        """
        target = context.get_en_passant_target()
        if target is None:
            return '-'
        ep_row, ep_col = target
        file_char = chr(ord('a') + ep_col)
        rank_char = str(8 - ep_row)
        return file_char + rank_char
