import typing as T
import numpy as np
import attr


@attr.frozen
class Fold:
    axis: str
    location: int


@attr.frozen
class Dot:
    x: int
    y: int

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.x}, {self.y})'


@attr.frozen
class Page:

    dots: T.Set[Dot] = attr.ib(converter=set)

    @property
    def num_dots(self):
        return len(self.dots)

    @property
    def size(self) -> T.Tuple[int, int]:
        """Dimensions of the page (needed to accomodate its dots) as x, y"""
        x_max = y_max = 0
        for dot in self.dots:
            x_max = max(x_max, dot.x)
            y_max = max(y_max, dot.y)
        return x_max +1, y_max + 1

    def display(self) -> None:
        """Print a neat-and-tidy ASCII representation of the page"""
        nx, ny = self.size

        data = [['.' for _ in range(nx)] for __ in range(ny)]
        
        for dot in self.dots:
            data[dot.y][dot.x] = '#'
        
        print()
        for row in data:
            print(''.join(row))
        print()

    def fold_me(self, instruction: Fold) -> 'Page':
        """Return a new folded version of this page"""

        if instruction.axis == 'x':
            new_dots = set()
            for dot in self.dots:
                if dot.x < instruction.location:
                    # left of the fold, add 
                    new_dots.add(dot)
                elif dot.x == instruction.location:
                    # on the fold, drop it
                    continue
                else:
                    # right of the fold, transform and add
                    new_dots.add(Dot(2*instruction.location - dot.x, dot.y))
            return Page(new_dots)

        elif instruction.axis == 'y':
            new_dots = set()
            for dot in self.dots:
                if dot.y < instruction.location:
                    # above the fold, add 
                    new_dots.add(dot)
                elif dot.y == instruction.location:
                    # on the fold, drop it
                    continue
                else:
                    # below the fold, transform and add
                    new_dots.add(Dot(dot.x, 2*instruction.location - dot.y))
            return Page(new_dots)

        raise ValueError(f"Can't handle instruction {instruction}")
    

def parse_input(filename: str) -> T.Tuple[Page, T.Tuple[Fold]]:
    
    with open(filename, 'r') as fp:
        
        pt1, pt2 = fp.read().split('\n\n')


    dots = []
    for line in pt1.strip().split('\n'):
        dots.append(
            Dot(*map(int, line.strip().split(',')))
        )

    folds = []
    for line in pt2.strip().split('\n'):
        axis, location = line.replace('fold along ', '').split('=')
        folds.append(Fold(axis, int(location)))

    return Page(dots), folds 
    



if __name__ == '__main__': 
    
    # input_file = 'test_input.txt'
    input_file = 'input.txt'


    print('puzzle 1 ----------')
    page, folds = parse_input(input_file)
    for fold in folds:
        page = page.fold_me(fold)
        print(f'{fold}: num_dots = {page.num_dots}')
    
    
