import typing as T
import dataclasses as dc
from itertools import cycle
import logging
from math import prod


log = logging.getLogger('roll100')


def deterministic_die(min_value: int = 1, max_value: int = 100) -> T.Iterator[int]:
    return cycle(range(min_value, max_value + 1))


BOARD = list(range(1, 11))
BOARD_LENGTH = len(BOARD)
WINNING_SCORE = 1000


class Pawn:
    
    id: int
    index: int
    score: int
    
    def __init__(self, id_: int, start_position: int):
        self.id = id_ 
        self.index = BOARD.index(start_position)
        self.score = 0

    @property
    def position(self) -> int:
        return BOARD[self.index]

    def move(self, die: T.Iterator[int]) -> int:
        """Move pawn and return the number of rolls"""
        step = next(die) + next(die) + next(die)
        self.index = (self.index + step) % BOARD_LENGTH
        self.score += self.position
        return 3

    @property
    def won(self) -> bool:
        return self.score >= WINNING_SCORE

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id}, position={self.position}, score={self.score})'


def deterministic_game(starts: T.List[int]) -> T.Tuple[T.List[Pawn], int]:
    """Return players sorted by final score and the total number of
    turns at the end of a deterministic game
    """
    die = deterministic_die()
    pawns = [Pawn(i, x) for i, x in enumerate(starts)]

    roll_count = 0
    for pawn in cycle(pawns):

        roll_count += pawn.move(die)
        log.info(f'{pawn}')

        if pawn.won:
            log.info('Player {pawn.id} wins!')
            break

    return sorted(pawns, key=lambda x: x.score), roll_count
    
    
if __name__ == '__main__':    

    logging.basicConfig(level=logging.INFO)

    print('test 1 ----------')
    players, rolls = deterministic_game([4, 8])
    print(f'Losing score * number of rolls = {players[0].score * rolls}')
    
    print('puzzle 1 ----------')
    players, rolls = deterministic_game([8, 2])
    print(f'Losing score * number of rolls = {players[0].score * rolls}')
