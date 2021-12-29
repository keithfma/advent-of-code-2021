import dataclasses as dc
from enum import Enum
import typing as T
import re
import numpy as np
import math
from pdb import set_trace


@dc.dataclass(frozen=True)
class Range:

    min: int
    max: int

    def __post_init__(self):
        if self.min > self.max:
            raise ValueError('Range is out of order')

    @property
    def npts(self) -> int:
        return self.max - self.min + 1

    def contains(self, other: 'Range') -> bool:
        return self.min <= other.min and self.max >= other.max

    def intersects(self, other: 'Range') -> bool:
        return self.min <= other.max and self.max >= other.min

    def intersection(self, other: 'Range') -> T.Optional['Range']:
        if self.intersects(other):
            return self.__class__(max(self.min, other.min), min(self.max, other.max))
        return None

    def split(self) -> T.Tuple['Range', 'Range']:
        if self.npts == 1:
            raise ValueError(f'Cannot split single point range {self}')
        cls = self.__class__
        lower = cls(self.min, self.min + self.npts // 2 - 1)
        upper = cls(lower.max + 1, self.max)
        return lower, upper

    def __repr__(self):
        return f'{self.__class__.__name__}({self.min}, {self.max})'


@dc.dataclass(frozen=True)
class Region:

    x: Range
    y: Range
    z: Range
    
    def contains(self, other: 'Region') -> bool:
        return self.x.contains(other.x) and self.y.contains(other.y) and self.z.contains(other.z)
    
    def intersects(self, other: 'Region') -> bool:
        return self.x.intersects(other.x) and self.y.intersects(other.y) and self.z.intersects(other.z)
    
    def intersection(self, other: 'Region') -> T.Optional['Region']:
        if self.intersects(other):
            return self.__class__(
                self.x.intersection(other.x), self.y.intersection(other.y), self.z.intersection(other.z)
            )
        return None

    @property
    def npts(self) -> int:
        return self.x.npts * self.y.npts * self.z.npts

    def split(self) -> T.Tuple['Region', ...]:
        """Split region into 8 equal-size subregions"""

        subs = []
        for x_range in self.x.split():
            for y_range in self.y.split():
                for z_range in self.z.split():
                    subs.append(self.__class__(x_range, y_range, z_range))

        # ensure equal size
        if len({sub.npts for sub in subs}) != 1:
            raise ValueError('Expect all subregions to be the same size!')
        
        return tuple(subs)

Instruction = T.Tuple[bool, Region]


def parse_input(filename: str) -> T.List[Instruction]:
    pattern = re.compile(r'^x=(-?\d+)..(-?\d+),y=(-?\d+)..(-?\d+),z=(-?\d+)..(-?\d+)')
    data = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            state_txt, bounds_txt = line.strip().split(' ')
            state = True if state_txt == 'on' else False
            bounds = [int(x) for x in pattern.match(bounds_txt).groups()]
            region = Region(Range(*bounds[:2]), Range(*bounds[2:4]), Range(*bounds[4:]))
            data.append((state,region))
    return data


def get_bounding_region(steps: T.List[Instruction]) -> Region:
    x = [float('inf'), -float('inf')]
    y = [float('inf'), -float('inf')]
    z = [float('inf'), -float('inf')]
    for _, region in steps:
        x[0] = min(x[0], region.x.min)
        y[0] = min(y[0], region.y.min)
        z[0] = min(z[0], region.z.min)
        x[1] = max(x[1], region.x.max)
        y[1] = max(y[1], region.y.max)
        z[1] = max(z[1], region.z.max)
    return Region(Range(*x), Range(*y), Range(*z))


def reboot_array(steps: T.List[Instruction]) -> int:
    """Naive reboot using a full array"""
    
    # init reactor array and corresponding index functions
    bnds = get_bounding_region(steps)
    
    reactor = np.zeros(
        (bnds.x.max - bnds.x.min + 1, bnds.y.max - bnds.y.min + 1, bnds.z.max - bnds.z.min + 1),
        dtype=np.bool_
    )
    
    def xidx(value: int) -> int:
        return value - bnds.x.min
     
    def yidx(value: int) -> int:
        return value - bnds.y.min
        
    def zidx(value: int) -> int:
        return value - bnds.z.min
    
    # apply instruction steps
    for state, region in steps:
        reactor[
            xidx(region.x.min) : xidx(region.x.max) + 1,
            yidx(region.y.min) : yidx(region.y.max) + 1,
            zidx(region.z.min) : zidx(region.z.max) + 1
        ] = state

    return reactor.sum()


@dc.dataclass
class OctNode:
    region: Region
    value: T.Optional[bool] = None
    children: T.Optional[T.Tuple['OctNode', ...]] = dc.field(repr=False, default=None)
    
    @property
    def is_leaf(self):
        if self.value is None:
            if self.children is None:
                raise ValueError('What am I?')
            return False
        else:
            if self.children is not None:
                raise ValueError('What am I?')
            return True

    def _split_range(): 
        raise NotImplementedError

    def split(self):
        """Break a leaf node into 8 smaller child leaf nodes"""
        if self.children is not None:
            raise ValueError("Can't split a node that already has children!")
        
        # create 8 children with same value as this newly-minted parent
        _children = []
        for region in self.region.split():
            _children.append(self.__class__(region=region, value=self.value))

        # update the parent
        self.value = None
        self.children = tuple(_children)

    def update(self, value, region):
        if region.intersects(self.region):
            if region.contains(self.region): 
                # set value and remove any children (the region is constant-valued now)
                self.value = value
                self.children = None
            else:
                # create children if needed
                if self.is_leaf:
                    self.split()
                # call update on all children
                for child in self.children:
                    child.update(value, region)
        else:
            # nothing to do if the region does not intersect
            pass

    def nonzero(self) -> int:
        """Return non-zero points in the tree under this node"""
        if self.is_leaf:
            if self.value is True:
                return self.region.npts
            return 0

        return sum(child.nonzero() for child in self.children)


def reboot_octree(steps: T.List[Instruction]) -> int:

    # define octree root node, which:
    #   + must cover the full area that the reboot instructions apply to, 
    #   + must have the number of points in each dimension as power of 2  
    #   + have the same number of points in each dimension
    bounds = get_bounding_region(steps)
    npts = max([bounds.x.npts, bounds.y.npts, bounds.z.npts])
    npts = 2**math.ceil(math.log(npts, 2))
    root = OctNode(
        region=Region(
            Range(bounds.x.min, bounds.x.max + (npts - bounds.x.npts)),
            Range(bounds.y.min, bounds.y.max + (npts - bounds.y.npts)),
            Range(bounds.z.min, bounds.z.max + (npts - bounds.z.npts)),
        ),
        value=False,
        children=None
    )

    # apply all reboot instructions
    for state, region in steps:
        print((state, region))
        root.update(state, region)

    # count non-zero volume
    return root.nonzero()
            

def reboot_geom(steps: T.List[Instruction]) -> int:

    # store list of (values, regions) representing the state of the reactor, this
    #   list includes the regions specified by our instructions as well as corrections
    #   to adjust for overlaps 
    reactor: T.List[T.Tuple[bool, Region]] = []

    # add each instruction region to the reactor in order
    for this_value, this_region in steps:

        # compute overlapping regions and the required adjustment for each,the adjustment
        #   is the overlapping region with the opposite value as the region
        #   it overlaps (i.e., the overlapping region is toggled). 
        # note that these adjustments may themselves be adjusted by later additions, and 
        #   so they are included in the normal reactor list 
        intersections = []
        for value, region in reactor:
            intersection = this_region.intersection(region)
            if intersection is not None:
                intersections.append((not value, intersection))
        
        reactor.extend(intersections)

        # positive regions are always added, for negative regions, we only want to add
        #   bits where they intersect other regions (and we already did so)
        if this_value is True:
            reactor.append((this_value, this_region))

    # compute volume from the reactor state
    volume = 0
    for value, region in reactor:
        sign = 1 if value else -1
        this_volume = sign*region.npts
        volume += this_volume

    return volume


if __name__ == '__main__':
    
    print('test 1 (array) -----------')
    instructions = parse_input('test_input_1.txt')
    cubes_on = reboot_array(instructions)
    print(f'{cubes_on} cubes are on')
    print()
    
    print('test 2 (array) -----------')
    instructions = parse_input('test_input_2.txt')
    cubes_on = reboot_array(instructions[:-2])
    print(f'{cubes_on} cubes are on')
    print()

    print('puzzle 1 (array) -----------')
    instructions = parse_input('input.txt')
    cubes_on = reboot_array(instructions[:20])
    print(f'{cubes_on} cubes are on')
    print()

    # Array is too big for any larger problems, abort!

    # print('test 1 (octree) -----------')
    # instructions = parse_input('test_input_1.txt')
    # cubes_on = reboot_octree(instructions)
    # print(f'{cubes_on} cubes are on')
    # print()

    # print('test 2 (octree) -----------')
    # instructions = parse_input('test_input_2.txt')
    # cubes_on = reboot_octree(instructions[:-2])
    # print(f'{cubes_on} cubes are on')
    # print()

    # Octree is deadly slow for any larger problems, abort!

    print('test 1 (geom) -----------')
    instructions = parse_input('test_input_1.txt')
    cubes_on = reboot_geom(instructions)
    print(f'{cubes_on} cubes are on')
    print()

    print('test 2 (geom) -----------')
    instructions = parse_input('test_input_2.txt')[:-2]
    cubes_on = reboot_geom(instructions)
    print(f'{cubes_on} cubes are on')
    print()

    print('puzzle 1 (geom) -----------')
    instructions = parse_input('input.txt')
    cubes_on = reboot_geom(instructions[:20])
    print(f'{cubes_on} cubes are on')
    print()

    print('test 3 (geom) -----------')
    instructions = parse_input('test_input_3.txt')
    cubes_on = reboot_geom(instructions)
    print(f'{cubes_on} cubes are on')
    print()

    print('puzzle 2 (geom) -----------')
    instructions = parse_input('input.txt')
    cubes_on = reboot_geom(instructions)
    print(f'{cubes_on} cubes are on')
    print()

