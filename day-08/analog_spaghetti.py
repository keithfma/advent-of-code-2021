import typing as T
import attr
import collections
from pprint import pprint


ABC = 'abcdefg'


@attr.frozen()
class Signal:
    """Represents a signal sent to a 7-segment display as a set of characters
    """
    segments: T.FrozenSet[str] = attr.ib(converter=frozenset)
    
    def __len__(self):
        return len(self.segments)

    def __repr__(self):
        segments_str = ''.join([x if x in self.segments else '_' for x in ABC]) 
        return f"{self.__class__.__name__}('{segments_str}')"


def exactly_one(obj):
    if len(obj) != 1:
        raise ValueError('One thing only, please!')
    if isinstance(obj, list):
        return obj[0]
    elif isinstance(obj, (set, frozenset)):
        return list(obj)[0]
    raise ValueError('What is this thing?')


@attr.s
class Display:
    """Represents a display, which has a set of the possible digit signals
    and a set of output signals to decode
    """
    digits: T.List[Signal] = attr.ib()
    outputs: T.List[Signal] = attr.ib()
    translation_map: T.Dict[Signal, int] = attr.ib()

    @translation_map.default
    def _build_translation(self) -> T.Dict[Signal, int]:

        # numbers to signals
        number_map: T.Dict[int, Signal] = dict()
        
        # display segment tags to "true" segment tags
        segment_map: T.Dict[str, str] = dict()
        
        # populate translations for digits with unique number of segments
        for digit in self.digits:
            if len(digit) == 2:
                number_map[1] = digit
            elif len(digit) == 3:
                number_map[7] = digit
            elif len(digit) == 4:
                number_map[4] = digit
            elif len(digit) == 7:
                number_map[8] = digit

        # TODO: can get away with just storing segment f, no map

        # segment 'a' is the set difference between known numbers 7 and 1
        options = number_map[7].segments - number_map[1].segments
        segment_map['a'] = exactly_one(options)

        # number 6 is the only length-6 signal that does not contain the number 1
        options = [s for s in self.digits if len(s) == 6 and not s.segments > number_map[1].segments] 
        number_map[6] = exactly_one(options)

        # The difference between number 1 and number 6 is segment 'c'
        options = number_map[1].segments - number_map[6].segments
        segment_c = exactly_one(options)

        # segments e & g are left from 8 - 4 - 7
        # then, the only length-6 signal that contains both is the number 0
        e_and_g = number_map[8].segments - (number_map[4].segments.union(number_map[7].segments))
        options = [s for s in self.digits if len(s) == 6 and s not in number_map.values() and s.segments > e_and_g]
        number_map[0] = exactly_one(options)

        # the last length-6 digit must be 9
        options = [s for s in self.digits if len(s) == 6 and s not in number_map.values()]
        number_map[9] = exactly_one(options)

        # 3 is the only length-5 digit that contains 1
        options = [s for s in self.digits if len(s) == 5 and s.segments > number_map[1].segments]
        number_map[3] = exactly_one(options)

        # 2 is the only remaining length-5 digit that contains 'c'
        options = [s for s in self.digits if len(s) == 5 and s not in number_map.values() and segment_c in s.segments]
        number_map[2] = exactly_one(options)

        # 5 is the only remaining length-5 digit
        options = [s for s in self.digits if len(s) == 5 and s not in number_map.values()]
        number_map[5] = exactly_one(options)

        # invert numbers_map to get translation table
        return {v: k for k, v in number_map.items()}

    def translate(self) -> int:
        """Translate each output signal and return the secret value"""
        secret_value = 0 
        num_output_places = len(self.outputs)
        for idx, output in enumerate(self.outputs, 1):
            secret_value += self.translation_map[output] * 10**(num_output_places - idx)
        return secret_value


def parse_input(filename: str) -> T.List[Display]:
    displays = [] 
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            parsed = [[Signal(set(y)) for y in x.strip().split(' ')] for x in line.strip().split('|')]
            displays.append(Display(*parsed))
    return displays


def count_1478(display: Display) -> int:
    """Count the number of that have easily-identified digits 1, 4, 7, or 8
    """
    unique_lengths = {2, 3, 4, 7}
    return sum(1 if len(x) in unique_lengths else 0 for x in display.outputs) 



if __name__ == '__main__':

    # input_file = 'test_input.txt'
    input_file = 'input.txt'
    displays = parse_input(input_file)
    
    print('puzzle 1 ----------')
    total = sum(count_1478(x) for x in displays)
    print(f'The number of easily-identified output digits is: {total}')
            
    print('puzzle 2 ----------')
    total = sum(d.translate() for d in displays)
    print(f'The sum of the displays is: {total}')
    

    
