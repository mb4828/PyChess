"""Game-wide constants for PGChess: window settings, board dimensions, asset paths, and custom events."""
import pygame


# ==== Window ==== #

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
WINDOW_COLOR = (200, 200, 200)

# ==== Custom Pygame Events ==== #

EVENT_WHITE_WINS = pygame.USEREVENT + 1
EVENT_BLACK_WINS = pygame.USEREVENT + 2
EVENT_DRAW = pygame.USEREVENT + 3
EVENT_PROMOTION = pygame.USEREVENT + 4
EVENT_COMPUTER_MOVE = pygame.USEREVENT + 5

# ==== Board ==== #

BOARD_WIDTH = 8
BOARD_HEIGHT = 8

SQ_HEIGHT = 75
SQ_LIGHT_COLOR = (232, 233, 212)
SQ_DARK_COLOR = (66, 148, 98)
SQ_HIGHLIGHT_COLOR = (255, 255, 51)
SQ_HIGHLIGHT_ALPHA = 127
SQ_HINT_COLOR = (100, 100, 100)
SQ_HINT_ALPHA = 127

# ==== Image Asset Paths ==== #

PATH_LOGO = 'assets/images/pgchess-full.png'
PATH_ICON = 'assets/images/pgchess.png'
PATH_KL = 'assets/images/white_king.png'
PATH_KD = 'assets/images/black_king.png'
PATH_QL = 'assets/images/white_queen.png'
PATH_QD = 'assets/images/black_queen.png'
PATH_BL = 'assets/images/white_bishop.png'
PATH_BD = 'assets/images/black_bishop.png'
PATH_NL = 'assets/images/white_knight.png'
PATH_ND = 'assets/images/black_knight.png'
PATH_RL = 'assets/images/white_rook.png'
PATH_RD = 'assets/images/black_rook.png'
PATH_PL = 'assets/images/white_pawn.png'
PATH_PD = 'assets/images/black_pawn.png'

# ==== Sound Asset Paths ==== #

PATH_GAME_START = 'assets/sounds/game_start.wav'
PATH_GAME_OVER = 'assets/sounds/game_over.wav'
PATH_ERROR = 'assets/sounds/error.wav'
PATH_PIECE_MOVE = 'assets/sounds/piece_move.wav'
PATH_PIECE_MOVE_2 = 'assets/sounds/piece_move_2.wav'
PATH_PIECE_CAPTURE = 'assets/sounds/piece_capture.wav'
PATH_PIECE_CHECK = 'assets/sounds/piece_check.wav'
PATH_MENU_CLICK = 'assets/sounds/drum_stick.mp3'
PATH_MENU_CONFIRM = 'assets/sounds/interface_click.wav'
