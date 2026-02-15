"""
Player vs. player (PVP) game
"""

from pychess.game.game import Game


class PVPGame(Game):
    def __init__(self, window):
        super().__init__(window)
