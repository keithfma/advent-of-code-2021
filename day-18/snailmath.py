import typing as T
from dataclasses import dataclass, field
import dataclasses as dc
import json
import re
from math import floor, ceil
import logging
from pdb import set_trace
from functools import reduce
from copy import deepcopy


log = logging.getLogger('snailmath')


@dc.dataclass
class Node:
    
    value: T.Optional[int]
    left: T.Optional['Node']
    right: T.Optional['Node']

    @property
    def is_pair(self) -> bool:
        return self.left is not None and self.right is not None

    @property
    def is_regular(self) -> bool:
        return self.value is not None

    @property
    def magnitude(self) -> int:
        if self.is_regular:
            return self.value
        return 3*self.left.magnitude + 2*self.right.magnitude

    @property
    def format(self) -> str:
        if self.is_regular:
            return str(self.value)
        return f'[{self.left.format},{self.right.format}]'
    
    def __repr__(self) -> str:
        if self.is_regular:
            return f'{self.__class__.__name__}({self.value})'
        else:
            return f'{self.__class__.__name__}({self.left}, {self.right})'


@dc.dataclass
class SnailNumber:
    
    root: Node

    @classmethod
    def parse(cls, txt: str) -> 'SnailNumber':
        return cls(cls._parse_node(json.loads(txt)))

    @classmethod
    def _parse_node(cls, data: T.Union[int, T.List]) -> Node:
        if isinstance(data, int):
            node = Node(data, None, None)
        else:
            node = Node(None, cls._parse_node(data[0]), cls._parse_node(data[1]))
        return node

    def _explode(self) -> bool:
        """Return True if a pair was exploded, else False"""


        # first pass: find first node to explode and explode it
        nodes, depths = in_order(self.root)
        exploded = False
        for node, depth in zip(nodes, depths):
            if node.is_pair and depth >= 4:

                if node.left.is_pair or node.right.is_pair:
                    raise ValueError('Expect to explode only pairs of regular numbers')

                exploded = True
                left_value = node.left.value
                right_value = node.right.value
                # set_trace()

                node.left = None
                node.right = None
                node.value = 0
                exploded_node = node  # so we can find it later
                
                break

        if exploded is True:

            # second pass: increment the regular numbers adjacent to the exploded node

            nodes, _ = in_order(self.root)
            
            # find the exploded node and split the ordered node list
            for idx in range(len(nodes) + 1):  # blow up if we don't find it

                if nodes[idx] is exploded_node:
                    # this is the node we exploded
                    before = nodes[:idx]
                    after = nodes[idx+1:]
                    break

            for node in reversed(before):
                if node.is_regular:
                    node.value += left_value
                    break
            
            for node in after:
                if node.is_regular:
                    node.value += right_value
                    break

            log.debug('Exploded: %s', self.format)

        return exploded 

    def _reduce(self):
        """Explode and split until you can't no more"""
        while True:
            if self._explode():
                continue
            if self._split():
                continue
            break

    def __add__(self, other: 'SnailNumber') -> 'SnailNumber':
        added = self.__class__(
            Node(
                None,
                deepcopy(self.root),
                deepcopy(other.root),
            )
        )       
        log.debug('Added: %s', added.format)
        added._reduce()
        return added

    def _split(self) -> bool:
        """Return True if a value was split, else False"""
        nodes, _ = in_order(self.root)
        
        split = False
        for node in nodes:
            if node.is_regular and node.value >= 10:
                split = True
                node.left = Node(floor(node.value / 2), None, None)
                node.right = Node(ceil(node.value / 2), None, None)
                node.value = None
                break

        if split:
            log.debug('Split: %s', self.format)
        return split

    @property
    def magnitude(self) -> int:
        return self.root.magnitude
        
    @property
    def format(self) -> str:
        return f'{self.root.format}'


def in_order(start: Node, depth: int = 0) -> T.Tuple[T.List[int], T.List[int]]:
    """Return in-order traversal of nodes and the depth of each in the tree"""

    this_node = [start]
    this_depth = [depth]

    if start.is_regular:
        return this_node, this_depth

    left_nodes, left_depths = in_order(start.left, depth+1)
    right_nodes, right_depths = in_order(start.right, depth+1)
    
    return left_nodes + this_node + right_nodes, left_depths + this_depth + right_depths


def parse_input(filename: str) -> T.List[SnailNumber]:
    data = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            data.append(SnailNumber.parse(line.strip()))
    return data


def reduce_numbers(numbers: T.List[SnailNumber]) -> SnailNumber:
    return reduce(lambda x, y: x + y, numbers)


# FIXME: fails because nodes are shared, so that reducing the result of an addition modifies the original
def maximum_magnitude(numbers: T.List[SnailNumber]) -> int:
    output = 0
    for ii, number_i in enumerate(numbers):
        for jj, number_j in enumerate(numbers):
            if number_i == number_j:
                continue
            magnitude = (number_i + number_j).magnitude
            output = max(output, magnitude)

            log.debug('i: %s', number_i.format)
            log.debug('j: %s', number_j.format)
            log.debug('mag: %i', magnitude)
            log.debug('')

    return output 


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    
    # print('test 1 ----------')
    # test_1_numbers = parse_input('test_input_1.txt')
    # test_1_observed= reduce_numbers(test_1_numbers)
    # test_1_expected = SnailNumber.parse('[[[[5,0],[7,4]],[5,5]],[6,6]]')
    # print(f'Number matched: {test_1_observed == test_1_expected}')
    # print()

    # print('test 2 ----------')
    # test_2_numbers = parse_input('test_input_2.txt')
    # test_2_observed= reduce_numbers(test_2_numbers)
    # test_2_expected = SnailNumber.parse('[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]')
    # print(f'Number matched: {test_2_observed == test_2_expected}')
    # print()

    # print('test 3 ----------')
    # test_3_numbers = parse_input('test_input_3.txt')
    # test_3_observed= reduce_numbers(test_3_numbers)
    # test_3_expected = SnailNumber.parse('[[[[6,6],[7,6]],[[7,7],[7,0]]],[[[7,7],[7,7]],[[7,8],[9,9]]]]')
    # print(f'Number matched: {test_3_observed == test_3_expected}')
    # print(f'Magnitude matched: {test_3_observed.magnitude == 4140}')
    # print()
    
    print('puzzle 1 ----------')
    input_numbers = parse_input('input.txt')
    result_1 = reduce_numbers(input_numbers)
    print(f'Magnitude: {result_1.magnitude}')
    print()

    # print('test 4 ----------')
    # test_4_numbers = parse_input('test_input_3.txt')  # reused the same input
    # test_4_observed = maximum_magnitude(test_4_numbers)
    # print(f'Magnitude matched: {test_4_observed== 3993}')
    # print()

    print('puzzle 2 ----------')
    input_numbers = parse_input('input.txt')
    result_2 = maximum_magnitude(input_numbers)
    print(f'Maximum pair-wise magnitude: {result_2}')
    print()
