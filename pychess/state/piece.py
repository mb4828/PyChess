"""Chess piece code constants."""
from enum import StrEnum


class Piece(StrEnum):
    """Two-character piece codes used to identify pieces on the board.

    The first character is the piece type:
        k = king, q = queen, r = rook, b = bishop, n = knight, p = pawn

    The second character is the color:
        l = light (white), d = dark (black)

    Because Piece is a StrEnum, each member compares equal to its string value:
        Piece.KL == 'kl'  # True
    """

    KL = 'kl'
    KD = 'kd'
    QL = 'ql'
    QD = 'qd'
    RL = 'rl'
    RD = 'rd'
    BL = 'bl'
    BD = 'bd'
    NL = 'nl'
    ND = 'nd'
    PL = 'pl'
    PD = 'pd'
