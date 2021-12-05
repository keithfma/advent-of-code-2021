import numpy as np
from typing import List, Tuple


# INPUT_FILE = 'test_input.txt'
INPUT_FILE = 'input.txt'


class BingoBoard:

    numbers: np.ndarray
    marks: np.ndarray

    def __init__(self, _id: int, _numbers: List[List[int]]):
        self.id = _id
        self.numbers = np.array(_numbers, dtype='uint8')
        self.marks = np.zeros_like(self.numbers, dtype='bool')

    @property
    def complete(self):
        return any(np.any(np.all(self.marks, axis=ax)) for ax in (0, 1))

    def mark(self, value):
        self.marks[self.numbers == value] = True

    def sum_unmarked_numbers(self) -> int:
        return self.numbers[~self.marks].sum()

    def __repr__(self):
        return f'BingoBoard(id={self.id})'
    

def parse_input(filename: str) -> Tuple[List[int], List[BingoBoard]]:
    
    with open(filename, 'r') as fp:

        # first read comma-separated list of numbers to call
        call_sequence = [int(x) for x in fp.readline().strip().split(',')]

        # read the rest and split into boards
        fp.readline()  # skip one newling
        boards_txt = fp.read().split('\n\n')

        # create BingoBoard objects
        boards = []

        for board_id, board_txt in enumerate(boards_txt, 1):
            numbers = []

            for row_txt in board_txt.split('\n'):
                row_numbers = [int(x) for x in row_txt.split(' ') if x]
                if row_numbers: 
                    numbers.append(row_numbers)

            if numbers:
                boards.append(BingoBoard(board_id, numbers))

    
    return call_sequence, boards


def playtime(call_sequence: List[int], bingo_boards: List[BingoBoard]) -> int:

    for call in calls:
        for board in boards:
            board.mark(call)
            if board.complete:
                print(f'Board {board} done!')
                return board.sum_unmarked_numbers()*call
    raise ValueError('No one won?')


def find_the_loser(call_sequence: List[int], bingo_boards: List[BingoBoard]) -> int:

    remaining_boards = set(bingo_boards)
    
    for call in calls:
        winners = set()
        for board in remaining_boards:
            board.mark(call)
            if board.complete:
                print(f'{board} complete!')
                winners.add(board)

        remaining_boards = remaining_boards.difference(winners)
        if not remaining_boards:
            return board.sum_unmarked_numbers()*call




if __name__ == '__main__':

    calls, boards = parse_input(INPUT_FILE)
    result = playtime(calls, boards)
    print('puzzle 1 ----------')
    print(f'result = {result}')
    print()

    calls, boards = parse_input(INPUT_FILE)  # need fresh boards!
    result = find_the_loser(calls, boards)
    print('puzzle 2 ----------')
    print(f'result = {result}')
    print()
