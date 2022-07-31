from enum import Enum

import pygame

import constants
from game.game_utils import get_resource_path
from game.menus import StartMenu, PauseMenu, GameOverMenu
from game.pvp import PVPGame


class GameState(Enum):
    START = 1
    PAUSE = 2
    PVP = 3
    GAME_OVER = 4


class PyChess:
    window = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    game_state = GameState.START
    running = True
    dragging = False

    game = None
    start_menu = None
    pause_menu = None
    game_over_menu = None

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('PyChess')
        pygame.display.set_icon(pygame.image.load(get_resource_path(constants.PATH_KL)))
        self.start_menu = StartMenu(self.start_pvp_game, self.quit_game)
        self.pause_menu = PauseMenu(lambda: self.set_game_state(GameState.PVP),
                                    lambda: self.set_game_state(GameState.START))
        self.game_over_menu = GameOverMenu(lambda: self.set_game_state(GameState.START))
        self.main()

    def set_game_state(self, state):
        self.game_state = state

    def start_pvp_game(self):
        self.game = PVPGame(self.window)
        self.game_state = GameState.PVP

    def quit_game(self):
        self.running = False

    def main(self):
        while self.running:
            # handle user interactions
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    # quit the game
                    self.quit_game()
                elif event.type == pygame.KEYDOWN and event.key == pygame.locals.K_ESCAPE and \
                        self.game_state == GameState.PVP:
                    # pause the game
                    self.game_state = GameState.PAUSE
                elif self.game and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # start of click and drag
                    self.dragging = True
                    y, x = event.pos
                    self.game.drag_start(x, y)
                elif self.game and event.type == pygame.MOUSEMOTION and self.dragging:
                    # mouse movement during click and drag
                    y, x = event.pos
                    self.game.drag_continue(x, y)
                elif self.game and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    # end of click and drag
                    self.dragging = False
                    self.game.drag_stop()
                elif event.type == constants.EVENT_WHITE_WINS:
                    # white wins the game
                    self.game_state = GameState.GAME_OVER
                    self.game_over_menu.set_winner(True)
                    self.white_wins = True
                elif event.type == constants.EVENT_BLACK_WINS:
                    # black wins the game
                    self.game_state = GameState.GAME_OVER
                    self.game_over_menu.set_winner(False)

            # draw graphics
            self.window.fill(constants.WINDOW_COLOR)
            if self.game:
                # draw game board
                self.game.draw()
            if self.game_state == GameState.START:
                # draw start menu
                self.start_menu.draw(self.window, events)
            if self.game_state == GameState.PAUSE:
                # draw pause menu
                self.pause_menu.draw(self.window, events)
            if self.game_state == GameState.GAME_OVER:
                # draw game over menu
                self.game_over_menu.draw(self.window, events)
            pygame.display.update()
            self.clock.tick(60)  # max 60 FPS

        # cleanup on exit
        pygame.quit()
        pygame.mixer.quit()
        quit()


if __name__ == '__main__':
    PyChess()
