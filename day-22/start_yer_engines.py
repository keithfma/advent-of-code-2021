import dataclasses as dc
from enum import Enum
import typing as T
import re
import numpy as np


@dc.dataclass
class Region:

    x_min: int
    x_max: int
    y_min: int
    y_max: int
    z_min: int
    z_max: int
    
    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'({self.x_min}, {self.x_max}), ' 
            f'({self.y_min}, {self.y_max}), ' 
            f'({self.z_min}, {self.z_max}))' 
        )
   

class State(Enum):
    OFF = 'off'
    ON = 'on'


@dc.dataclass
class Instruction:
    state: State
    region: Region


def parse_input(filename: str) -> T.List[Instruction]:
    pattern = re.compile(r'^x=(-?\d+)..(-?\d+),y=(-?\d+)..(-?\d+),z=(-?\d+)..(-?\d+)')
    data = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            state_txt, region_txt = line.strip().split(' ')
            state = State(state_txt)
            region = Region(*map(int, pattern.match(region_txt).groups()))
            data.append(Instruction(state, region))
            
    return data


def reboot_array(steps: T.List[Instruction]) -> int:
    """Naive reboot using a sparse array"""
    
    # init reactor array and corresponding index functions
    x_min = y_min = z_min = x_max = y_max = z_max = 0
    for step in steps:
        x_min = min(x_min, step.region.x_min)
        y_min = min(y_min, step.region.y_min)
        z_min = min(z_min, step.region.z_min)
        x_max = max(x_max, step.region.x_max)
        y_max = max(y_max, step.region.y_max)
        z_max = max(z_max, step.region.z_max)
    
    # scipy sparse arrays are 2D only, tried this 'sparse' package which is terribly slow, forget about it.
    # reactor = sparse.DOK(
    #     shape=(x_max - x_min + 1, y_max - y_min + 1, z_max - z_min + 1),
    #     dtype=np.bool_
    # )
    reactor = np.zeros(
        (x_max - x_min + 1, y_max - y_min + 1, z_max - z_min + 1),
        dtype=np.bool_
    )
    
    def xidx(value: int) -> int:
        return value - x_min
     
    def yidx(value: int) -> int:
        return value - y_min
        
    def zidx(value: int) -> int:
        return value - z_min
    
    # apply instruction steps
    for step in steps:
        print(step)
        reactor[
            xidx(step.region.x_min) : xidx(step.region.x_max) + 1,
            yidx(step.region.y_min) : yidx(step.region.y_max) + 1,
            zidx(step.region.z_min) : zidx(step.region.z_max) + 1
        ] = True if step.state is State.ON else False

    return reactor.sum()
    
        


if __name__ == '__main__':
    
    print('test 1 -----------')
    instructions = parse_input('test_input_1.txt')
    cubes_on = reboot_array(instructions)
    print(f'{cubes_on} cubes are on')
    print()
    
    print('test 2 -----------')
    instructions = parse_input('test_input_2.txt')
    cubes_on = reboot_array(instructions[:-2])
    print(f'{cubes_on} cubes are on')
    print()

    print('puzzle 1 -----------')
    instructions = parse_input('input.txt')
    cubes_on = reboot_array(instructions[:20])
    print(f'{cubes_on} cubes are on')
    print()
