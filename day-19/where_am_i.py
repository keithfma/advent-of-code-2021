import typing as T
import numpy as np
import dataclasses as dc
import re
import itertools
from pdb import set_trace


class NoMatchError(Exception):
    """Unable to match scanner to reference"""


def orientations() -> T.Iterator[T.Tuple[np.ndarray, np.ndarray]]:
    """Yield all 24 possible orientations as axis permutation vectors and axis sign vectors
    """
    orders = list(itertools.permutations([0, 1, 2]))
    signs = [[a, b, c] for a in [1, -1] for b in [1, -1] for c in [1, -1]]
    for order, sign in itertools.product(orders, signs):
        yield np.array(order), np.array(sign)


@dc.dataclass
class Scanner:

    # Just an ID for the scanner, helpful for debugging test cases mostly
    id: int

    # the (known) location of this scanner, or None
    location: np.ndarray 

    # Array in which each row contains the x, y, z position of a beacon detected
    #   by this scanner
    beacons: np.ndarray = dc.field(repr=False)

    @property
    def relative(self) -> bool:
        """True if the beacon coordinates are relative to the scanner position, 
        or False if they have been converted to absolute coordinates
        """
        return self.location is None

    def match(self, other: 'Scanner', threshold: int = 12) -> 'Scanner':

        if self.relative:
            raise ValueError('Cannot match to a scanner with relative coordinates')

        if not other.relative:
            raise ValueError("Don't try to orient a scanner that already has a known location")

        # iterate over all possible orientations
        for order, sign in orientations():

            # apply rotation
            beacons = other.beacons[:, order] * sign

            # check all offsets between the reference and other scanner that would bring at least
            #   one beacon into alignment -- this is the set of all pair-wise offsets between the
            #   two beacon locations. If we find any offset that appears 'threshold' times, we 
            #   have a match
            offsets = (beacons.reshape((-1, 1, 3)) - self.beacons.reshape((1, -1, 3))).reshape((-1, 3))
            unique_offsets, unique_offset_counts = np.unique(offsets, axis=0, return_counts=True)
            
            match_idx = np.flatnonzero(unique_offset_counts >= threshold)
            if match_idx.size == 0:
                # no matching offset for this orientation
                pass

            elif match_idx.size == 1:

                match_offset = unique_offsets[match_idx[0], :]
                
                print(f'Match for order: {order}, sign: {sign}, offset: {match_offset}')

                return self.__class__(
                    id=other.id,
                    location=match_offset,
                    beacons=beacons - match_offset
                )

            else:
                raise ValueError('Multiple matches?')

        raise NoMatchError
        
        

def parse_input(filename: str) -> T.List[Scanner]:

    with open(filename, 'r') as fp:
        blocks = fp.read().split('\n\n')

    id_pattern = re.compile('^--- scanner (\d+) ---')

    output = []
    for block in blocks:
        lines = block.strip().split('\n')
        id_ = int(id_pattern.match(lines[0]).group(1))
        beacons = [
            [int(x) for x in line.split(',')]
            for line in lines[1:]
        ]
        obj = Scanner(
            id=id_, location=None, beacons=np.array(beacons, dtype=np.int32)
        )
        output.append(obj)

    return output 


def match_all(scanners: T.List[Scanner], threshold: int = 12):
    """Orient all scanners relative to the first in the list"""

    # assume first scanner orientation is truth
    scanners[0].location = np.zeros((1, 3), dtype=np.int32)      

    # orient all other scanners relative to the first
    completed = []
    references = [scanners[0]]
    unknowns = scanners[1:]

    while references:
        
        reference = references.pop()

        still_unknowns = []
        while unknowns:
            unknown = unknowns.pop()
            try:
                known = reference.match(unknown, threshold)
                references.append(known)
            except NoMatchError:
                # better luck next time!
                still_unknowns.append(unknown)
        
        unknowns = still_unknowns
        completed.append(reference)

    return completed


def beacon_count(scanners: T.List[Scanner]) -> int:

    if any(x.relative for x in scanners):
        raise ValueError('Cannot count until all scanners are oriented') 

    unique_beacons = np.unique(
        np.concatenate([x.beacons for x in scanners], axis=0),
        axis=0
    )

    return unique_beacons.shape[0]


def maximum_manhattan_distance(scanners: T.List[Scanner]) -> int:

    if any(x.relative for x in scanners):
        raise ValueError('Cannot find distances until all scanners are oriented') 

    # note: use the same broadcasting trick we used for computing offsets in the 
    #   Scanner.match function. This does all the calculation 2x, but who cares?

    locations = np.concatenate([x.location.reshape((1, -1)) for x in scanners], axis=0)
    
    pairwise_absolute_difference = np.absolute(
        locations.reshape((-1, 1, 3)) - locations.reshape((1, -1, 3))
    ).reshape((-1, 3))

    manhattan_distance = np.sum(pairwise_absolute_difference, axis=1)

    return manhattan_distance.max()
    

if __name__ == '__main__':
    
    print('test 1 ----------')
    test_1 = parse_input('test_input_1.txt')
    test_1 = match_all(test_1, 3)
    print(f'Found {beacon_count(test_1)} beacons')
    print()
    
    print('test 2 ----------')
    test_2 = parse_input('test_input_2.txt')
    test_2 = match_all(test_2, 6)
    print(f'Found {beacon_count(test_2)} beacons')
    print()
    
    print('test 3 ----------')
    test_3 = parse_input('test_input_3.txt')
    test_3 = match_all(test_3, 12)
    print(f'Found {beacon_count(test_3)} beacons')
    print()

    print('puzzle 1 ----------')
    puzzle_1 = parse_input('input.txt')
    puzzle_1 = match_all(puzzle_1, 12)
    print(f'Found {beacon_count(puzzle_1)} beacons')
    print()

    print('puzzle 2 ----------')
    # note: we can re-use the oriented scanners from puzzle 1
    print(f'Maximum (manhattan) distance between scanners: {maximum_manhattan_distance(puzzle_1)}')
    print()
