import numpy as np
import typing as T
from collections import Counter
from math import prod
from pdb import set_trace


def parse_input(filename: str) -> np.ndarray:
    """Return input array, padded with 0s"""
    with open(filename, 'r') as fp:
        data = []
        for line in fp.readlines():
            data.append(list(line.strip()))
    data_array = np.array(data, dtype='uint8')
    return np.pad(data_array, 1, 'constant', constant_values=0)


def timestep(power: np.ndarray) -> T.Tuple[np.ndarray, int]:
    """Advance powerpus state by one timestep, return new powerpus state and number of flashes
    """
    nr, nc = power.shape

    # "flashed" array tracks which octopi have flashed this turn
    #   the boundary pad is treated as though it contains "flashed" octopuses
    flashed = np.ones((nr, nc), dtype='bool')
    flashed[1:nr-1, 1:nc-1] = False

    # increment the power level of all octopi (i.e., move time forward)
    power = power + 1

    # resolve flashes and their cascades
    flash_count = 0

    while True:
        new_flashes = (power > 9) & ~flashed
        new_flash_count = np.sum(new_flashes)

        if new_flash_count == 0: 
            break
        
        flash_count += new_flash_count

        rows, cols = np.nonzero(new_flashes)
        
        for row, col in zip(rows, cols):
            power[row-1:row+2, col-1:col+2] += 1

        flashed[new_flashes] = True

    # reset all flashed octopuses
    power[flashed] = 0
    
    return power, flash_count



def total_flashes(power: np.ndarray, num_steps: int) -> int:
    
    modeled_power = np.copy(power)
    flash_count = 0

    for _ in range(num_steps):
        modeled_power, new_flash_count = timestep(modeled_power)
        flash_count += new_flash_count

    return flash_count


def first_sync_flash(power: np.ndarray, max_num_steps: int) -> int:
    
    modeled_power = np.copy(power)
    nr, nc = power.shape
    num_octopi = (nr-2)*(nc-2)  # account for pad

    for t in range(max_num_steps):
        modeled_power, flash_count = timestep(modeled_power)
        print((t, flash_count, num_octopi))
        if flash_count == num_octopi:
            return t+1

    raise ValueError('they never did!')



if __name__ == '__main__':
    
    input_file = 'test_input.txt'
    input_file = 'input.txt'

    octopi = parse_input(input_file)

    print('puzzle 1 ----------')
    num_time_steps = 100
    print(f'number of flashes after {num_time_steps} steps: {total_flashes(octopi, num_time_steps)}')


    print('puzzle 2 ----------')
    print(f'The first sychronized flash occurs at steps: {first_sync_flash(octopi, 1000)}')
    
