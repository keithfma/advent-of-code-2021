import typing as T
from bitarray import bitarray
from bitarray.util import ba2int


# INPUT_FILE = 'test_input.txt'
INPUT_FILE = 'input.txt'

# read the input as a list of binary arrays
data = []
with open(INPUT_FILE, 'r') as fp:
    for line in fp.readlines():
        data.append(bitarray(line.strip()))


def most_common(candidates: T.List[bitarray]) -> bitarray:
    """Utility returning the most likely bits over the input candidates"""
    num_candidates = len(candidates)
    num_digits = len(candidates[0])  # assume all same length
   
    counts = [0 for _ in range(num_digits)]
    for candidate in candidates:
        for idx in range(num_digits):
            counts[idx] += candidate[idx]

    # note: round() uses "bankers rounding", so we have to do it the hard way
    half_num_candidates = num_candidates/2
    most = bitarray()
    for idx in range(num_digits):
        most.append(1 if counts[idx] >= half_num_candidates else 0)

    return most


def find_rating(candidates, invert: bool = False):
    idx = 0
    matches = candidates 

    while True:
        key = most_common(matches)
        if invert:
            key = ~key

        next_matches = [x for x in matches if x[idx] == key[idx]]

        if len(next_matches) == 1:
            return next_matches[0]
        elif len(next_matches) == 0:
            raise ValueError('No match left?')

        matches = next_matches
        idx += 1


oxygen = ba2int(find_rating(data))
co2 = ba2int(find_rating(data, invert=True))
    

print('puzzle 2 ----------')
print(f'oxygen = {oxygen}, co2 = {co2}, oxygen*co2 = {oxygen*co2}')
print()


    
