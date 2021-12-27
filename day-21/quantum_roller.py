import typing as T
import numpy as np
from collections import defaultdict
import math


MIN_SPACE = 1
MAX_SPACE = 10
BOARD = list(range(MIN_SPACE, MAX_SPACE+1))
NUM_SPACES = len(BOARD)
WINNING_SCORE = 21 


def turns_to_win(start_position: int) -> T.Dict[int, int]:
    """Return lookup mapping number of turns-to-win to the number of
    possible games that ended at that turn number
    """
    # track possible "universes" in an array where the row represents the
    #   current position on the board, and the column represents the current
    #   score, and the value represents the number of "universes" where the 
    #   player is in that (position, score) state
    universes = np.zeros((len(BOARD), WINNING_SCORE), dtype=np.uint)

    # initial state has one universe with a single player with score 0
    universes[BOARD.index(start_position), 0] = 1

    # maps turns-to-win -> universe count, the output of this function
    winners: T.Mapping[int, int] = defaultdict(lambda: 0)

    # update the board until all universes have completed the game
    turn = 0
    while True:

        # next turn!
        turn += 1
        updated = np.zeros_like(universes)

        # iterate over quantum rolls
        for roll_1 in range(1, 4):
            for roll_2 in range(1, 4):
                for roll_3 in range(1, 4):
                    
                    rolled = roll_1 + roll_2 + roll_3
            
                    for curr_position_idx in range(NUM_SPACES):
                        # changing position shifts row down (wrapping at the end)
                        # changing score shifts columns right (winning at the end)
                        next_position_idx = (curr_position_idx + rolled) % NUM_SPACES
                        score_delta = next_position_idx + MIN_SPACE  # used for scoring

                        winners[turn] += np.sum(universes[curr_position_idx, -score_delta:])
                        updated[next_position_idx, score_delta:] += universes[curr_position_idx, :-score_delta]

                        # winners[turn] += np.sum(universes[curr_position_idx, -score_delta:])
                        # updated[next_position_idx, score_delta:] += universes[curr_position_idx, :-score_delta]


        universes = updated
        print(f'turn: {turn}, active universes: {universes.sum()}, winners: {sum(winners.values())}')

        if universes.sum() == 0:
            # no universes remain where the player has not completed the game
            break

    out = np.zeros(turn, dtype=np.uint)
    for idx in range(turn):
        out[idx] = winners[idx+1]

    return out



def turns_to_win_alt(start_position: int) -> T.Dict[int, int]:
    """Return lookup mapping number of turns-to-win to the number of
    possible games that ended at that turn number
    """
    winners = defaultdict(lambda: 0)
    games = defaultdict(lambda: 0)

    turn = 0
    games[(start_position, 0)] = 1    

    while games:

        next_games = defaultdict(lambda: 0)
        for game, count in games.items():
            for roll_1 in range(1, 4):
                for roll_2 in range(1, 4):
                    for roll_3 in range(1, 4):
                        rolled = roll_1 + roll_2 + roll_3
                        next_position = (game[0] - MIN_SPACE + rolled) % NUM_SPACES + MIN_SPACE
                        next_score = game[1] + next_position
                        if next_score >= WINNING_SCORE:
                            winners[turn] += count
                        else:
                            next_games[(next_position, next_score)] += count
        games = next_games
        turn += 1

    return winners


# note: both turns_to_win functions appear to work, or, at least they agree.
# can't seem to go from that to an answer though!


from dataclasses import dataclass
import enum

class Player(enum.Enum):
    PLAYER_1 = 1
    PLAYER_2 = 2


@dataclass(frozen=True)
class Game:

    p1_idx: int  # position index
    p1_score: int 

    p2_idx: int  # position index
    p2_score: int 

    def p1_move(self, roll: int) -> 'Game':
        idx = (self.p1_idx + roll) % NUM_SPACES
        return self.__class__(
            idx, self.p1_score + idx + MIN_SPACE, self.p2_idx, self.p2_score
        )

    def p2_move(self, roll: int) -> 'Game':
        idx = (self.p2_idx + roll) % NUM_SPACES
        return self.__class__(
            self.p1_idx, self.p1_score, idx, self.p2_score + idx + MIN_SPACE
        )

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
        
        # TODO: could make this a loop using the enum

        # player 1 moves
        new_games = defaultdict(lambda: 0)
        for roll, roll_count in ROLL_COUNT:
            for game, game_count in games.items():
                new_game = game.p1_move(roll)
                if new_game.winner == Player.PLAYER_1:
                    winners[Player.PLAYER_1] += game_count * roll_count
                else:
                    new_games[new_game] += game_count * roll_count
        games = new_games

        # player 2 moves
        new_games = defaultdict(lambda: 0)
        for roll, roll_count in ROLL_COUNT:
            for game, game_count in games.items():
                new_game = game.p2_move(roll)
                if new_game.winner == Player.PLAYER_2:
                    winners[Player.PLAYER_2] += game_count * roll_count
                else:
                    new_games[new_game] += game_count * roll_count

        games = new_games

    return winners
        
        
if __name__ == '__main__':

    print('test 1 ----------')
    wins = universe_count(4, 8)
    print(wins)

    print('puzzle 1 ----------')
    wins = universe_count(8, 2)
    print(wins)
    
