import typing as T
from types import MappingProxyType


def parse_input(filename: str) -> T.List[str]:
    with open(filename, 'r') as fp:
        return [line.strip() for line in fp.readlines()]


OPENERS = MappingProxyType(
    {
        '(': ')',
        '[': ']',
        '{': '}',
        '<': '>',
    } 
)

INVALID_CHAR_SCORES = MappingProxyType(
    {
        None: 0,
        ')': 3,
        ']': 57,
        '}': 1197,
        '>': 25137,
    } 
)

SUFFIX_SCORES = MappingProxyType(
    {
        ')': 1,
        ']': 2,
        '}': 3,
        '>': 4,
    } 
)



def first_invalid_character(line: str) -> T.Optional[str]:
    """Return first invalid character, if any"""
    opened = []
    for char in line:
        if char in OPENERS:
            opened.append(char)
        else:
            if opened and char == OPENERS[opened[-1]]:
                opened.pop(-1)
            else:
                # this is the first invalid char!
                return char


def complete_suffix(line: str) -> T.Optional[str]:
    """Return missing suffix that makes the incomplete string valid"""
    # screen out invalid lines, isolate the un-completed prefix
    opened = []
    for char in line:
        if char in OPENERS:
            opened.append(char)
        else:
            if opened and char == OPENERS[opened[-1]]:
                # paired, remove from queue
                opened.pop(-1)
            else:
                # invalid, we are done here
                return None

    # complete each unpaired character
    suffix = []
    for char in reversed(opened):
        suffix.append(OPENERS[char])

    return ''.join(suffix)


def score_suffix(line: str) -> int:
    chars = complete_suffix(line)

    if chars is None:
        return 0

    score = 0
    for char in chars:
        score = score*5 + SUFFIX_SCORES[char]
    return score



if __name__ == '__main__':
    
    input_file = 'test_input.txt'
    input_file = 'input.txt'

    data = parse_input(input_file) 

    print('puzzle 1 ----------')
    invalid_line_score = sum(INVALID_CHAR_SCORES[first_invalid_character(x)] for x in data) 
    print(f'Score for invalid lines = {invalid_line_score}')

    print('puzzle 2 ----------')
    suffixes = [complete_suffix(x) for x in data]
    scores = [score_suffix(x) for x in data]
    sorted_scores = sorted(x for x in scores if x != 0)
    winning_score = sorted_scores[len(sorted_scores)//2]
    print(f'Score for line suffixes = {winning_score}')

