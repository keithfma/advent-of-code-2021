import numpy as np
import typing as T
from collections import Counter
from math import prod


def parse_input(filename: str) -> np.ndarray:
    """Return input array, padded with 9s"""
    with open(filename, 'r') as fp:
        data = []
        for line in fp.readlines():
            data.append(list(line.strip()))
    data_array = np.array(data, dtype='uint8')
    return np.pad(data_array, 1, 'constant', constant_values=9)


def local_minima(heights: np.ndarray) -> T.List[T.Tuple[int, int]]:
    kernel = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype='bool')
    minima = []
    
    # loop over interior points only
    for ii in range(1, heights.shape[0]-1): 
        for jj in range(1, heights.shape[1]-1):
            center = heights[ii, jj]    
            neighborhood = heights[ii-1:ii+2, jj-1:jj+2]
            if np.all(center < neighborhood[kernel]):
                minima.append((ii, jj))

    return minima


def total_risk(heights: np.ndarray) -> int:
    locations = local_minima(heights)
    return sum(heights[row, col] + 1 for row, col in locations)



def basins(heights: np.ndarray) -> np.ndarray:

    labels = np.zeros(heights.shape, dtype='int')
    queue = []

    def assign(this: T.Tuple[int, int], label: int):
        nonlocal labels
        nonlocal queue

        if labels[this] == 0 and heights[this] != 9:
            labels[this] = label 
            queue.extend([
                ((this[0] + 0, this[1] - 1), label),
                ((this[0] + 0, this[1] + 1), label),
                ((this[0] - 1, this[1] + 0), label),
                ((this[0] + 1, this[1] + 0), label),
            ])

        
    # 9s and only 9s are the ridges dividing the basins
    labels[heights == 9] = -1  

    # minima each define thier own basin
    minima = local_minima(heights)
    for label, location in enumerate(minima, 1):
        queue.append((location, label))    
        
    
    # label everything
    while queue:
        assign(*queue.pop())
        
    return labels


def basin_sizes(heights: np.ndarray) -> T.List[int]:

    basin_labels = basins(heights)
    counts = Counter(basin_labels.reshape(-1))
    del counts[-1]  # exclude ridges!
    return sorted(counts.values(), reverse=True)


if __name__ == '__main__':
    
    input_file = 'test_input.txt'
    input_file = 'input.txt'

    zz = parse_input(input_file)

    print('puzzle 1 ----------')
    print(f'Total risk at low points is: {total_risk(zz)}')
    print()

    print('puzzle 2 ----------')
    top_3_sizes = basin_sizes(zz)[0:3]
    print(f'Top 3 basin sizes: {top_3_sizes}')
    print(f'Product of top 3 sizes: {prod(top_3_sizes)}')
    print()

    
    

