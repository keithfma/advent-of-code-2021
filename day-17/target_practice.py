import re
import typing as T
from math import ceil, sqrt
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Range:
    min: int
    max: int
    

def get_target_limits(filename: str) -> T.Tuple[Range, Range]:
    with open(filename, 'r') as fp:
        txt = fp.read().strip()
    pattern = re.compile(r'target area: x=(-?\d+)..(-?\d+), y=(-?\d+)..(-?\d+)')
    xmin, xmax, ymin, ymax = map(int, pattern.match(txt).groups())
    return Range(xmin, xmax), Range(ymin, ymax)


def get_velocity_limits(target_x: Range, target_y: Range) -> T.Tuple[Range, Range]:
    """Compute range of initial velocities that can possibly hit the target
    """
    # check assumption
    if target_y.min < 0 and target_x.min > 0:
        ValueError('Assumption violated')

    # the fastest u just hits the far side of the target on the first shot
    u_max = target_x.max 

    # the slowest u just reaches the near side of the target as the velocity is reduced to 0
    # ...this happens when target_xmin = u_min*(u_min + 1)/2, a little quadratic formula magic gives
    # ...the expression below
    u_min = ceil(-0.5 + sqrt(0.25 + 2*target_x.min))

    # the minimum v shoots downwards fast enough to just hit the bottom of the target
    v_min = target_y.min

    # the maximum v returns to y==0 with a velocity fast enough to just hit the bottom of the 
    #   target. Note that all v0 > 0 return to y==0 exactly with next-step velocity of -(v0 + 1)    
    v_max = -target_y.min - 1

    return Range(u_min, u_max), Range(v_min, v_max)



def highest_y(target_y: Range) -> int:
    """Maximum height is achieved by the maximum initial v that hits the target, 
    and reaches a peak height at the sum of integers up to that initial v
    """
    return target_y.min*(target_y.min + 1) // 2


def total_hits(target_x_limits: Range, target_y_limits: Range, u_limits: Range, v_limits: Range) -> int:
    """Count of unique starting velocities that eventually hit the target
    """

    # check assumption
    if u_limits.min > 0:
        ValueError('Assumption violated')

    # x and u as row vectors
    u = np.arange(u_limits.min, u_limits.max + 1, 1, dtype=np.int32).reshape((1, -1))
    x = np.zeros_like(u)

    # y and v as column vectors
    v = np.arange(v_limits.min, v_limits.max + 1, 1, dtype=np.int32).reshape((-1, 1))
    y = np.zeros_like(v)

    # success matrix starts all False
    hits = np.zeros((v.size, u.size), dtype=np.bool_)
    
    # the last shot to hit is the one that arcs the highest first, it takes v0 + 1 steps to reach 
    #   its apex, the same to fall back to y == 0, and then one more step to hit the target
    max_num_steps = 2*v_limits.max + 3

    for _ in range(max_num_steps):

        # update positions
        x = x + u
        y = y + v

        # update hits by setting any initial u,v combination that yielded a hit to True
        x_on_target = np.logical_and(x >= target_x_limits.min, x <= target_x_limits.max) 
        y_on_target = np.logical_and(y >= target_y_limits.min, y <= target_y_limits.max) 
        hits = np.logical_or(hits, x_on_target*y_on_target)

        # update velocities for next step
        u = np.maximum(0, u - 1)
        v = v - 1

    return hits.sum()
    


if __name__ == '__main__': 
    
    input_file = 'test_input.txt'
    input_file = 'input.txt'

    x_lim, y_lim = get_target_limits(input_file)
    u_lim, v_lim = get_velocity_limits(x_lim, y_lim)

    print('puzzle 1 ----------')
    print(f'The highest reachable height is: {highest_y(y_lim)}')
    print()


    print('puzzle 2 -----------')
    print(f'There are {total_hits(x_lim, y_lim, u_lim, v_lim)} unique initial velocities that hit the target') 

    
    
