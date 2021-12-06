import typing as T
from copy import copy


INPUT = 'input.txt'
# INPUT = 'test_input.txt'


def parse_input(filename) -> T.List[int]:
    with open(INPUT, 'r') as fp: 
        return [int(x) for x in fp.read().split(',')]
        

def be_fruitful_and_multiply(fish: T.List[int], num_days: int) -> int:

    # each location in this "population" list contains the current count of fish
    #   whose timer is at that index, so [100, 0, 99] would represent a population
    #   with 100 fish at timer=0, and 99 fish at timer=2
    population = [0 for _ in range(9)]
    for this_fish in fish:
        population[this_fish] += 1

    for day in range(num_days):
        next_population = population[1:] + [population[0]]
        next_population[6] += population[0]
        population = next_population
        print(f'Day {day}, {sum(population)} fish') 

    return sum(population)



if __name__ == '__main__':
    
    fish = parse_input(INPUT)
    
    print('puzzle 1 ----------')
    num_days = 80
    count = be_fruitful_and_multiply(fish, num_days)
    print(f'After {num_days} days, there are {count} lanternfish')
    
    print('puzzle 2 ----------')
    num_days = 256 
    count = be_fruitful_and_multiply(fish, num_days)
    print(f'After {num_days} days, there are {count} lanternfish')
