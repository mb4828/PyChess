"""
Game constants
"""
VERSION = '2026.2.1'

WINDOW_WIDTH = 600  # width of the game window
WINDOW_HEIGHT = 600  # height of the game window
WINDOW_COLOR = (200, 200, 200)

EVENT_WHITE_WINS = 0  # event triggered when white wins
EVENT_BLACK_WINS = 1  # event triggered when black wins

BOARD_WIDTH = 8  # number of squares in a row
BOARD_HEIGHT = 8  # number of squares in a column

SQ_HEIGHT = 75  # Width / height of a square
SQ_LIGHT_COLOR = (220, 237, 255)  # Light square color
SQ_DARK_COLOR = (148, 176, 218)  # Dark square color
SQ_HIGHLIGHT_COLOR = (255, 255, 51)  # Highlighted overlay color
SQ_HIGHLIGHT_ALPHA = 127  # Highlighted overlay alpha
SQ_HINT_COLOR = (140, 140, 140)  # Hint overlay color
SQ_HINT_ALPHA = 127  # Hint overlay alpha

PATH_LOGO = 'assets/images/pychess.png'  # game logo
PATH_KL = 'assets/images/white_king.png'  # light king sprite
PATH_KD = 'assets/images/black_king.png'  # dark king sprite
PATH_QL = 'assets/images/white_queen.png'  # light queen sprite
PATH_QD = 'assets/images/black_queen.png'  # dark queen sprite
PATH_BL = 'assets/images/white_bishop.png'  # light bishop sprite
PATH_BD = 'assets/images/black_bishop.png'  # dark bishop sprite
PATH_NL = 'assets/images/white_knight.png'  # light knight sprite
PATH_ND = 'assets/images/black_knight.png'  # dark knight sprite
PATH_RL = 'assets/images/white_rook.png'  # light rook sprite
PATH_RD = 'assets/images/black_rook.png'  # dark rook sprite
PATH_PL = 'assets/images/white_pawn.png'  # light pawn sprite
PATH_PD = 'assets/images/black_pawn.png'  # dark pawn sprite

PATH_GAME_START = 'assets/sounds/game_start.wav'  # game start sound
PATH_GAME_OVER = 'assets/sounds/game_over.wav'  # game over sound
PATH_ERROR = 'assets/sounds/error.wav'  # error sound
PATH_PIECE_MOVE = 'assets/sounds/piece_move.wav'  # piece move sound
PATH_PIECE_MOVE_2 = 'assets/sounds/piece_move_2.wav'  # piece move sound 2
PATH_PIECE_CAPTURE = 'assets/sounds/piece_capture.wav'  # piece capture sound
PATH_PIECE_CHECK = 'assets/sounds/piece_check.wav'  # piece capture sound
