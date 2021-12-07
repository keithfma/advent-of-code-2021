import typing as T
from statistics import median

# INPUT = 'test_input.txt'
INPUT = 'input.txt'


def parse_input(filename) -> T.List[int]:
    with open(filename, 'r') as fp:
        return [int(x) for x in fp.read().strip().split(',')]


def simple_energy_cost(locations: T.List[int]) -> int:
    """The *median* is the optimal location, because it minimizes
    the sum of absolute errors. You might be thinking of using the mean,
    but this minimizes the sum of squared errors, and that ain't
    the problem we are solving

    The python statistics.median implementation uses the "mean of the
     middle two" in case of a tie, so we must round and cast to int
    """
    best = int(round(median(locations)))
    return sum(abs(x-best) for x in locations)


    mean_location = sum(locations)/len(locations)
    print(f'mean location={mean_location}')


def escalating_energy_cost(locations: T.List[int]) -> int:
    """Brute force! This will scale as O(n**2), which is OK since n is at most 1000
    If we needed to be faster, then we could start with the mean as an initial
    guess and then do some kind of gradient descent. It's just not worth it right now
    """
    min_loc = min(locations)
    max_loc = max(locations)
    
    # build a helper table to avoid repeated cost calculations
    # note: the cost function is the set of "triangular numbers", https://en.wikipedia.org/wiki/Triangular_number
    distance_to_cost = {dist: int(dist*(dist+1)/2) for dist in range(max_loc - min_loc + 1)}

    best_location = None
    best_cost = float('inf')
    for candidate in range(min_loc, max_loc+1):
        cost = sum(distance_to_cost[abs(x-candidate)] for x in locations)  
        # print(f'candidate={candidate}, cost={cost}')
        if cost < best_cost:
            best_location = candidate
            best_cost = cost
    
    # print(f'best location={best_location}, best cost={best_cost}')
    return best_cost
   
        



if __name__ == '__main__': 
    crabs = parse_input(INPUT)
    
    print('puzzle 1 ----------')
    energy = simple_energy_cost(crabs)
    print(f'Minimum energy needed is: {energy}')

    print('puzzle 1 2---------')
    energy = escalating_energy_cost(crabs)
    print(f'Minimum energy needed is: {energy}')
    
