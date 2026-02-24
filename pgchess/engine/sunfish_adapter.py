"""Sunfish chess engine adapter."""
import logging
import random
from typing import Dict, Optional, Tuple

from pgchess.engine import sunfish
from pgchess.engine.engine import EngineAdapter, FENConverter, Difficulty
from pgchess.state.game_context import GameContext
from pgchess.state.game_state import GameState

logger = logging.getLogger(__name__)


class SunfishAdapter(EngineAdapter):
    """Chess engine adapter backed by the vendored sunfish library.

    Converts PGChess game state to FEN, parses it into a sunfish
    :class:`~pgchess.engine.sunfish.Position`, runs iterative-deepening
    search to a difficulty-based depth limit, and returns the best move as
    PGChess board coordinates.

    Because PGChess always has the computer playing black, the board is rotated
    180° before the search so that sunfish treats the computer's pieces as its
    own (uppercase). The resulting move indices are un-rotated before rendering.

    Difficulty levels are based on search depth and blunder probability:
    - EASY: depth 2, 20% chance of playing the shallower depth-1 move as a blunder
    - MEDIUM: depth 3 with no blunders
    - HARD: depth 8 with no blunders
    """

    def get_best_move(
        self,
        state: GameState,
        context: GameContext,
    ) -> Tuple[int, int, int, int, str]:
        """Search the current position and return the best move as board coordinates.

        :param state: Current board state
        :param context: Current game context (castling rights, en passant, turn)
        :return: Tuple of ``(start_row, start_col, end_row, end_col, promotion)``
        """
        fen = FENConverter.to_fen(state, context)
        logger.debug("Engine FEN: %s", fen)
        pos, was_rotated = self._fen_to_position(fen)
        move = self._search(pos)
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

    def _search(self, pos: sunfish.Position) -> Optional[sunfish.Move]:
        """Run depth-limited iterative-deepening search with optional blunder.

        Collects the best move found at each search depth. For easy difficulty,
        occasionally returns the depth-1 move instead of the deeper best move,
        simulating a shallower (weaker) analysis.

        :param pos: Sunfish position to search from
        :return: Best :class:`~pgchess.engine.sunfish.Move` found, or occasionally
                 a shallower-depth move (if easy mode blunder triggers)
        """
        # Difficulty configuration: (max_depth, blunder_probability)
        # EASY uses depth 2 so depth-1 is available as a genuine weaker alternative.
        depth_configs = {
            Difficulty.EASY: (2, 0.2),
            Difficulty.MEDIUM: (3, 0.0),
            Difficulty.HARD: (8, 0.0),
        }
        max_depth, blunder_prob = depth_configs[self._difficulty]

        searcher = sunfish.Searcher()
        best_at_depth: Dict[int, Tuple[sunfish.Move, int]] = {}

        # Continue past max_depth until at least one valid move is found, ensuring
        # the engine never returns None on a losing position where gamma=0 finds nothing.
        for depth, _gamma, _score, move in searcher.search([pos]):
            if move is not None:
                best_at_depth[depth] = (move, _score)
            if depth >= max_depth and best_at_depth:
                break

        if not best_at_depth:
            return None

        final_depth = max(best_at_depth.keys())
        best_move, _best_score = best_at_depth[final_depth]

        # For easy difficulty, occasionally return the shallower depth's best move
        if blunder_prob > 0 and random.random() < blunder_prob:
            shallow_depth = final_depth - 1
            if shallow_depth in best_at_depth:
                shallow_move, _shallow_score = best_at_depth[shallow_depth]
                if shallow_move != best_move:
                    logger.debug(
                        "BLUNDER: Playing depth-%d move (score %s) instead of depth-%d best move (score %s)",
                        shallow_depth, _shallow_score, final_depth, _best_score,
                    )
                    return shallow_move

        return best_move

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
