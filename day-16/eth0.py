from bitarray import frozenbitarray, bitarray
from bitarray.util import hex2ba, ba2int
import dataclasses as dc 
import enum
import typing as T
from pdb import set_trace
from math import prod


ENDIAN = 'big'


class PacketType(enum.Enum):
    SUM = 0
    PRODUCT = 1
    MINIMUM = 2
    MAXIMUM = 3
    LITERAL = 4
    GREATER_THAN = 5
    LESS_THAN = 6
    EQUAL_TO = 7


@dc.dataclass(frozen=True)
class Header:

    version: int
    type: PacketType

    @classmethod
    def from_bits(cls, bits: bitarray, idx: int) -> T.Tuple['Header', int]:
        """Parse packet header from bits starting at index 'idx'
        Return the header and the index just after the end of the parsed header
        """
        version = ba2int(bits[idx:idx+3])
        type_ = PacketType(ba2int(bits[idx+3:idx+6]))
        return cls(version, type_), idx + 6


# TODO: just one class will do the trick you know...


@dc.dataclass
class Packet:

    header: Header
    parent: T.Optional['Packet'] = dc.field(repr=False)


@dc.dataclass
class LiteralPacket(Packet):

    value: int
    
    @classmethod
    def from_bits(cls, header: Header, bits: bitarray, idx: int, parent: T.Optional[Packet]) -> T.Tuple['LiteralPacket', T.Optional[int]]:
        """Parse literal packet with header 'header' and parent 'parent' starting at index 'idx'
        Return the packet and the index just after the end of the parsed packet (or None if this is the last packet)
        """
        value_bits = bitarray(endian=ENDIAN)
        while True:
            flag_bit = bits[idx] 
            value_bits.extend(bits[idx+1:idx+5])
            idx += 5
            if flag_bit == 0:
                break  # we just parsed the last digit

        return cls(header, parent, ba2int(value_bits)), idx 


@dc.dataclass
class OperatorPacket(Packet):

    children: T.List[Packet] = dc.field(repr=False)

    @property
    def value(self) -> int:

        if self.header.type == PacketType.SUM:
            return sum(c.value for c in self.children)

        if self.header.type == PacketType.PRODUCT:
            return prod(c.value for c in self.children)

        if self.header.type == PacketType.MINIMUM:
            return min(c.value for c in self.children)

        if self.header.type == PacketType.MAXIMUM:
            return max(c.value for c in self.children)

        if self.header.type == PacketType.GREATER_THAN:
            return self.children[0].value > self.children[1].value

        if self.header.type == PacketType.LESS_THAN:
            return self.children[0].value < self.children[1].value

        if self.header.type == PacketType.EQUAL_TO:
            return self.children[0].value == self.children[1].value

        raise ValueError(f'No operation defined for type: {self.header.type}')
    
    @classmethod
    def from_bits(cls, header: Header, bits: bitarray, idx: int, parent: T.Optional[Packet]) -> T.Tuple['OperatorPacket', T.Optional[int]]:
        """Parse operator packet with header 'header' and parent 'parent' starting at index 'idx'
        Return the packet and the index just after the end of the parsed packet (or None if this is the last packet)
        """
        self = cls(header, parent, children=[])

        length_type_id = bits[idx]
        idx += 1

        children = []

        if length_type_id == 0:
            # the next 15 bits are a number that represents the total length
            #   in bits of the sub-packets contained by this packet
            children_num_bits = ba2int(bits[idx:idx+15])
            idx += 15
            last_child_idx = idx + children_num_bits
            
            while idx < last_child_idx:
                child, idx = next_packet(bits, idx, self)
                self.children.append(child)

        else: 
            # the next 11 bits are a number that represents the number of
            #   sub-packets immediately contained by this packet
            num_child_packets = ba2int(bits[idx:idx+11])
            idx += 11

            for _ in range(num_child_packets):
                child, idx = next_packet(bits, idx, self)
                self.children.append(child)

        return self, idx


def next_packet(bits: bitarray, idx: int, parent: T.Optional[Packet]) -> T.Tuple[Packet, T.Optional[int]]:
    """Parse the next packet beginning at index 'idx' with optional parent packet 'parent'
    Return the packet and the index just after the end of the parsed packet, or None if that was the last packet
    """
    header, idx= Header.from_bits(bits, idx)
    
    if header.type == PacketType.LITERAL:
        packet_class = LiteralPacket
    else: 
        packet_class = OperatorPacket

    return packet_class.from_bits(header, bits, idx, parent)
    


def hex_to_bits(data_hex: str) -> frozenbitarray:
    return frozenbitarray(hex2ba(data_hex, endian=ENDIAN))


def hex_to_packet(data_hex: str) -> Packet:
    data_bits = hex_to_bits(data_hex)
    data_packet, _ = next_packet(data_bits, 0, None)
    return data_packet


def unpack_children(packet: Packet) -> T.List[Packet]:
    objs = [packet]
    if hasattr(packet, 'children'):
        for child in packet.children:
            objs.extend(unpack_children(child))
    return objs


def sum_versions(packet: Packet) -> int:
    return sum(p.header.version for p in unpack_children(packet))
        

if __name__ == '__main__':
    
    # test case 1: literal packet with known value
    test_1_hex = 'D2FE28'
    test_1 = hex_to_packet(test_1_hex)
    assert test_1.header.type == PacketType.LITERAL
    assert test_1.header.version == 6
    assert test_1.value == 2021

    # test case 2: operator packet with length-type-id 0 containing 2 subpackets
    test_2_hex = '38006F45291200'
    test_2 = hex_to_packet(test_2_hex)
    assert test_2.header.type == PacketType.LESS_THAN
    assert test_2.header.version == 1
    assert len(test_2.children) == 2
    for child, value in zip(test_2.children, [10, 20]):
        assert child.header.type == PacketType.LITERAL
        assert child.value == value


    # test case 3: operator packet with length-type-id 1 containing 3 subpackets
    test_3_hex = 'EE00D40C823060'
    test_3 = hex_to_packet(test_3_hex)
    assert test_3.header.type == PacketType.MAXIMUM
    assert test_3.header.version == 7
    assert len(test_3.children) == 3
    for child, value in zip(test_3.children, [1, 2, 3]):
        assert child.header.type == PacketType.LITERAL
        assert child.value == value

    # test case 4: operator >  operator > operator > literal value 
    print('test case 4 ----------')
    test_4_hex = '8A004A801A8002F478'
    test_4 = hex_to_packet(test_4_hex)
    print(f'Sum of version numbers: {sum_versions(test_4)}')
    print()

    
    print('puzzle 1----------')
    with open('input.txt', 'r') as fp:
        input_hex = fp.read().strip()
    input_packet = hex_to_packet(input_hex)
    print(f'Sum of version numbers: {sum_versions(input_packet)}')
    print()
    
    print('puzzle 2----------')
    print(f'Value of input packet is: {input_packet.value}')
    print()
    
