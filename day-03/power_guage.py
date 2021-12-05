import typing as T
from bitarray import bitarray
from bitarray.util import ba2int


INPUT_FILE = 'test_input.txt'
NUM_DIGITS = 5

#INPUT_FILE = 'input.txt'
#NUM_DIGITS = 12

# build an array containing the sum in each position
num_lines = 0
digit_sums = [0 for _ in range(NUM_DIGITS)]

with open(INPUT_FILE, 'r') as fp:
    for line in fp.readlines():
        num_lines += 1
        for idx in range(NUM_DIGITS):
            digit_sums[idx] += int(line[idx])

# build a bitarray by round to find the most common value 
most_common = bitarray(endian='big')
for digit_sum in digit_sums:
    most_common.append(round(digit_sum/num_lines))
least_common = ~most_common

# convert to integers
gamma = ba2int(most_common, signed=False)
epsilon = ba2int(least_common, signed=False)


print('puzzle 1 ----------')
print(f'gamma = {gamma}, epsilon = {epsilon}, gamma*epsilon = {gamma*epsilon}')
print()

