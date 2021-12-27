import typing as T
import numpy as np
from collections import defaultdict
import math
from dataclasses import dataclass
import enum


MIN_SPACE = 1
MAX_SPACE = 10
BOARD = list(range(MIN_SPACE, MAX_SPACE+1))
NUM_SPACES = len(BOARD)
WINNING_SCORE = 21 



class Player(enum.Enum):
    PLAYER_1 = 1
    PLAYER_2 = 2


@dataclass(frozen=True)
class Game:

    p1_idx: int  # position index
    p1_score: int 

    p2_idx: int  # position index
    p2_score: int 

    def move(self, player: Player, roll: int) -> 'Game':
        if player == Player.PLAYER_1:
            idx = (self.p1_idx + roll) % NUM_SPACES
            return self.__class__(
                idx, self.p1_score + idx + MIN_SPACE, self.p2_idx, self.p2_score
            )
        if player == Player.PLAYER_2:
            idx = (self.p2_idx + roll) % NUM_SPACES
            return self.__class__(
                self.p1_idx, self.p1_score, idx, self.p2_score + idx + MIN_SPACE
            )
        raise ValueError

    @property
    def winner(self):
        if self.p1_score >= WINNING_SCORE:
            return Player.PLAYER_1
        elif self.p2_score >= WINNING_SCORE:
            return Player.PLAYER_2
        return None


ROLL_COUNT = [(3,1),(4,3),(5,6),(6,7),(7,6),(8,3),(9,1)]


def universe_count(p1_start: int, p2_start: int):
    
    games = defaultdict(lambda: 0)
    games[Game(p1_start - 1, 0, p2_start - 1, 0)] = 1
    winners = {Player.PLAYER_1: 0, Player.PLAYER_2: 0}

    while games:
        
        for player in [Player.PLAYER_1, Player.PLAYER_2]:

            new_games = defaultdict(lambda: 0)

            for roll, roll_count in ROLL_COUNT:
                for game, game_count in games.items():
                    combo_count = game_count * roll_count
                    new_game = game.move(player, roll)
                    if new_game.winner == player:
                        winners[player] += combo_count
                    else:
                        new_games[new_game] += combo_count

            games = new_games

    return winners
        
        
if __name__ == '__main__':

    print('test 1 ----------')
    wins = universe_count(4, 8)
    print(wins)

    print('puzzle 1 ----------')
    wins = universe_count(8, 2)
    print(wins)
    
