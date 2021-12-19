import re
import typing as T


def parse_input(filename: str) -> T.Tuple[int, int, int, int]:
    with open(filename, 'r') as fp:
        txt = fp.read().strip()
    pattern = re.compile(r'target area: x=(-?\d+)..(-?\d+), y=(-?\d+)..(-?\d+)')
    xmin, xmax, ymin, ymax = map(int, pattern.match(txt).groups())
    return xmin, xmax, ymin, ymax


def highest_y(target_ymin) -> int:
    # + Assumes that target_y_min is negative
    # + All shots with a positive v0 eventually return back to y == 0, and when they do,
    #   their velocity is -v0 
    # + The highest shot will have the largest v0
    # + Thus, we want the shot where the falling shot just barely lands in the target area, 
    #   which is at -(v0 + 1) == target_y_min
    # + The maximum hieght of a shot is a simple function of v0, the sum of all integers up to v0
    if target_ymin >= 0:
        ValueError('Assumption violated')
    v0 = -target_ymin - 1
    return v0*(v0+1) // 2
    


if __name__ == '__main__': 
    
    input_file = 'test_input.txt'
    # input_file = 'test_input.txt'

    x_min, x_max, y_min, y_max = parse_input(input_file)

    print('puzzle 1 ----------')
    print(f'The highest reachable height is: {highest_y(y_min)}')
    print()

    
    
