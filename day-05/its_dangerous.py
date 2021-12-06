import attr
import typing as T
import re
from collections import Counter


INPUT = 'input.txt'
# INPUT = 'test_input.txt'


@attr.frozen
class Point:
    x: int = attr.ib(converter=int)
    y: int = attr.ib(converter=int)


@attr.frozen(auto_attribs=True)
class Vent:
    a: Point
    b: Point 

    @property
    def is_vertical(self) -> bool:
        return self.a.x == self.b.x

    @property
    def is_horizontal(self) -> bool:
        return self.a.y == self.b.y

    @property
    def is_diagonal(self):
        return not self.is_vertical and not self.is_horizontal 

    def points(self, exclude_diagonal: bool) -> T.List[Point]:
        """Return all (integer-coordinate) points along this vent
        """

        # note to future-keith: you could have consolidated these cases pretty easily, 
        #   but it is not really worth doing so right now.

        if self.is_vertical:
            x = self.a.x
            y0, y1 = sorted([self.a.y, self.b.y])
            return [Point(x, y) for y in range(y0, y1 + 1)]

        if self.is_horizontal:
            x0, x1 = sorted([self.a.x, self.b.x])
            y = self.a.y
            return [Point(x, y) for x in range(x0, x1 + 1)]

        if self.is_diagonal:

            if exclude_diagonal:
                return [] 
            
            x_step = 1 if self.b.x > self.a.x else -1
            y_step = 1 if self.b.y > self.a.y else -1
            return [
                Point(x, y) for x, y in zip(
                    range(self.a.x, self.b.x + x_step, x_step),
                    range(self.a.y, self.b.y + y_step, y_step)
                ) 
            ]
            # print('')
            # print(f'{self}, {points}') 
            # print('')
            # return points


def parse_input(filename: str) -> T.List[Vent]:
    pattern = re.compile(r'(\d+),(\d+) -> (\d+),(\d+)')
    objs = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            match = pattern.match(line)
            objs.append(
                Vent(Point(match[1], match[2]), Point(match[3], match[4]))
            )
    return objs


def count_intersections(_vents: T.List[Vent], exclude_diagonal: bool) -> int:
    count = Counter() 
    for vent in _vents:
        count.update(vent.points(exclude_diagonal))
    return sum(x > 1 for x in count.values())


if __name__ == '__main__':
    
    vents = parse_input(INPUT)

    print('puzzle 1 ----------')
    num_intersections_1 = count_intersections(vents, exclude_diagonal=True)
    print(f'Num points with more than one vent: {num_intersections_1}')
    print()

    print('puzzle 2 ----------')
    num_intersections_2 = count_intersections(vents, exclude_diagonal=False)
    print(f'Num points with more than one vent (including diagonals): {num_intersections_2}')
    print()
    
