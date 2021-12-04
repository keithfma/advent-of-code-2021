"""Count the number of times a sequence of integer depth readings increases
"""
from pathlib import Path

INPUT_FILE = Path('input.txt')


# read the test sequence
with open(INPUT_FILE, 'r') as fp:
    depths = [int(x) for x in fp]

count = 0
idx = 1
while idx < len(depths):
    count += int(depths[idx] > depths[idx-1])
    idx += 1 

print(f'Depth increased {count} times')

