"""Sunfish chess engine adapter."""
import logging
import time
from typing import Optional, Tuple

from pgchess.engine import sunfish
from pgchess.engine.engine import EngineAdapter, FENConverter
from pgchess.state.game_context import GameContext
from pgchess.state.game_state import GameState

logger = logging.getLogger(__name__)


class SunfishAdapter(EngineAdapter):
    """Chess engine adapter backed by the vendored sunfish library.

    Converts PGChess game state to FEN, parses it into a sunfish
    :class:`~pgchess.engine.sunfish.Position`, runs iterative-deepening
    search for the given time budget, and returns the best move as PGChess
    board coordinates.

    Because PGChess always has the computer playing black, the board is rotated
    180° before the search so that sunfish treats the computer's pieces as its
    own (uppercase). The resulting move indices are un-rotated before rendering.
    """

    def get_best_move(
        self,
        state: GameState,
        context: GameContext,
        move_time_seconds: float = 1.0,
    ) -> Tuple[int, int, int, int, str]:
        """Search the current position and return the best move as board coordinates.

        :param state: Current board state
        :param context: Current game context (castling rights, en passant, turn)
        :param move_time_seconds: Maximum search time in seconds
        :return: Tuple of ``(start_row, start_col, end_row, end_col, promotion)``
        """
        fen = FENConverter.to_fen(state, context)
        logger.debug("Engine FEN: %s", fen)
        pos, was_rotated = self._fen_to_position(fen)
        move = self._search(pos, move_time_seconds)
        if move is None:
            logger.warning("Sunfish returned no move for FEN: %s", fen)
            return (0, 0, 0, 0, '')
        lan = self._move_to_lan(move, was_rotated)
        logger.debug("Engine LAN: %s", lan)
        return FENConverter.from_lan(lan)

    # ==== FEN parsing ==== #

    def _fen_to_position(self, fen: str) -> Tuple[sunfish.Position, bool]:
        """Parse a FEN string into a sunfish Position, rotating if it is black to move.

        :param fen: FEN string
        :return: ``(position, was_rotated)`` — *was_rotated* is True when the board
                 was flipped to present black's pieces as the active side
        """
        parts = fen.split()
        board_fen, active, castling, ep_str = parts[0], parts[1], parts[2], parts[3]

        # Sunfish always searches as white; rotate the board when it's black's turn
        # so that black's pieces become uppercase (the active player).
        was_rotated = active == 'b'

        board = self._build_board_string(board_fen)
        if was_rotated:
            board = board[::-1].swapcase()

        wc, bc = self._parse_castling(castling, was_rotated)
        ep = self._parse_ep(ep_str, was_rotated)

        return sunfish.Position(board, 0, wc, bc, ep, 0), was_rotated

    def _build_board_string(self, board_fen: str) -> str:
        """Convert the piece-placement field of a FEN string to sunfish's 120-char format.

        :param board_fen: Piece placement portion of FEN (e.g. ``'rnbqkbnr/pppppppp/8/...'``)
        :return: 120-character padded board string
        """
        # Two padding rows top and bottom; each rank is space-prefixed and newline-terminated.
        rows = ['         \n', '         \n']
        for rank_str in board_fen.split('/'):
            row = ' '
            for ch in rank_str:
                row += '.' * int(ch) if ch.isdigit() else ch
            rows.append(row + '\n')
        rows += ['         \n', '         \n']
        return ''.join(rows)

    def _parse_castling(
        self, castling: str, was_rotated: bool
    ) -> Tuple[Tuple[bool, bool], Tuple[bool, bool]]:
        """Derive sunfish wc/bc castling tuples from a FEN castling field.

        Sunfish's wc is [west/A1-side, east/H1-side] for the current player.
        After board rotation (black to move):
        - wc[0] = black's kingside (maps to A1 after flip) = 'k'
        - wc[1] = black's queenside (maps to H1 after flip) = 'q'
        - bc[0] = white's queenside (A8 after flip) = 'Q'
        - bc[1] = white's kingside (H8 after flip) = 'K'

        :param castling: FEN castling field, e.g. ``'KQkq'`` or ``'-'``
        :param was_rotated: True if the board was rotated (black to move)
        :return: ``(wc, bc)`` tuples of booleans
        """
        if was_rotated:
            # After 180° rotation black's kingside is near A1, queenside near H1
            wc = ('k' in castling, 'q' in castling)
            bc = ('Q' in castling, 'K' in castling)
        else:
            wc = ('Q' in castling, 'K' in castling)
            bc = ('k' in castling, 'q' in castling)
        return wc, bc

    def _parse_ep(self, ep_str: str, was_rotated: bool) -> int:
        """Convert a FEN en-passant square to a sunfish board index.

        :param ep_str: FEN en-passant field, e.g. ``'e3'`` or ``'-'``
        :param was_rotated: True if the board was rotated (black to move)
        :return: Sunfish board index, or 0 if none
        """
        if ep_str == '-':
            return 0
        ep_index = sunfish.parse(ep_str)
        return (119 - ep_index) if was_rotated else ep_index

    # ==== Search ==== #

    def _search(self, pos: sunfish.Position, time_limit: float) -> Optional[sunfish.Move]:
        """Run time-limited iterative-deepening search.

        :param pos: Sunfish position to search from
        :param time_limit: Wall-clock seconds to spend searching
        :return: Best :class:`~pgchess.engine.sunfish.Move` found, or None
        """
        searcher = sunfish.Searcher()
        best: Optional[sunfish.Move] = None
        start = time.monotonic()

        # Single-entry history — no threefold-repetition detection.
        for _depth, _gamma, _score, move in searcher.search([pos]):
            if move is not None:
                best = move
            if time.monotonic() - start >= time_limit:
                break

        return best

    # ==== Move rendering ==== #

    def _move_to_lan(self, move: sunfish.Move, was_rotated: bool) -> str:
        """Convert a sunfish Move to Long Algebraic Notation.

        If the board was rotated before search, un-rotate the move indices so
        they map back to the original (white-on-bottom) perspective.

        :param move: Sunfish Move namedtuple
        :param was_rotated: True if the board was rotated before search
        :return: LAN string, e.g. ``'e7e5'`` or ``'e7e8q'``
        """
        i, j = (119 - move.i, 119 - move.j) if was_rotated else (move.i, move.j)
        return sunfish.render(i) + sunfish.render(j) + move.prom.lower()
