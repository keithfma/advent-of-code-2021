import typing as T
from collections import Counter 
from dataclasses import dataclass
from copy import copy


@dataclass(frozen=True, order=True)
class Pair:
    
    elements: str

    def __post_init__(self):
        if len(self.elements) != 2:
            raise ValueError(f'Expect a pair of elements, got: "{self.elements}"')
    
    def insert(self, element: str) -> T.Tuple['Pair', 'Pair']:
        cls = self.__class__
        return cls(self.elements[0] + element), cls(element + self.elements[1])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.elements}')"



@dataclass(frozen=True)
class Rule:
    
    pair: Pair
    element: str


@dataclass(frozen=True)
class Polymer:

    first: Pair 
    last: Pair
    counts: T.Mapping[Pair, int]
    rules: T.Tuple[Rule]

    @classmethod
    def from_file(cls, filename: str) -> 'Polymer':

        # read in data
        with open(filename, 'r') as fp:
            template = fp.readline().strip()
            fp.readline()  # skip empty line
            lines = fp.readlines()

        # parse first and last pairs
        _first = Pair(template[:2])
        _last = Pair(template[-2:])

        # count all pairs
        _counts = Counter()
        for a, b in zip(template[:-1], template[1:]):
            _counts[Pair(a+b)] += 1

        # parse rules
        rules = []
        for line in lines:
            elements, element = map(lambda x: x.strip(), line.split('->'))
            rules.append(Rule(Pair(elements), element))

        return cls(_first, _last, _counts, tuple(rules))

    def print_counts(self):
        for pair, count in sorted(self.counts.items()):
            if count: 
                print(f'{pair.elements}: {count}')
        print()
    

    def step(self) -> 'Polymer':

        # copy current first, last, and counts 
        new_first = self.first
        new_last = self.last
        new_counts = copy(self.counts)

        # reset counts for pairs that will be split
        for rule in self.rules:
            new_counts[rule.pair] = 0
            
        for rule in self.rules:

            # increment counts for new pairs created by splitting the old ones
            for new_pair in rule.pair.insert(rule.element):
                new_counts[new_pair] += self.counts[rule.pair] 

            # update first and last
            if rule.pair == self.first:
                new_first = rule.pair.insert(rule.element)[0]

            if rule.pair == self.last:
                new_last = rule.pair.insert(rule.element)[1]

        return self.__class__(new_first, new_last, new_counts, self.rules)

    def score(self) -> int:
        """NOTE: scoring is a little tricky since we have not stored the polymer string"""
        
        char_counts = Counter()
        for pair, count in self.counts.items():
            for char in pair.elements:
                char_counts[char] += count
        
        # all characters are double-counted except the first and last, adjust these
        #   edge cases so that everything is double counted
        char_counts[self.first.elements[0]] += 1
        char_counts[self.last.elements[1]] += 1
        
        sorted_char_counts = sorted(
            char_counts.items(), key=lambda x: x[1], reverse=True
        )

        return (sorted_char_counts[0][1] - sorted_char_counts[-1][1]) // 2


if __name__ == '__main__':
    
    input_file = 'test_input.txt'
    input_file = 'input.txt'


    print('puzzle 1 ----------')
    polymer = Polymer.from_file(input_file)
    num_steps = 10
    for _ in range(num_steps):
        polymer = polymer.step()
    print(f'Score after {num_steps} steps: {polymer.score()}')
    print()

    print('puzzle 2 ----------')
    polymer = Polymer.from_file(input_file)
    num_steps = 40
    for _ in range(num_steps):
        polymer = polymer.step()
    print(f'Score after {num_steps} steps: {polymer.score()}')
    print()
