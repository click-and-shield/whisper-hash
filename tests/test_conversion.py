# Usage:
# python3 -m unittest -v test_conversion.py

import unittest
import sys
import os
from typing import cast

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.conversion import Conversion
from whisper import Int64, Bit, Int16

class TestConversion(unittest.TestCase):

    def test_int64_to_bit_list(self) -> None:
        inputs: list[Int64] = cast(list[Int64], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        expecteds: list[list[Bit]] = cast(list[list[Bit]], [
            [0] * 64,                           # 0
            [0] * 63 + [1],                     # 1
            [0] * 62 + [1] + [0],               # 2
            [0] * 62 + [1] + [1],               # 3
            [0] * 61 + [1] + [0] + [0],         # 4
            [0] * 61 + [1] + [0] + [1],         # 5
            [0] * 61 + [1] + [1] + [0],         # 6
            [0] * 61 + [1] + [1] + [1],         # 7
            [0] * 60 + [1] + [0] + [0] + [0],   # 8
            [0] * 60 + [1] + [0] + [0] + [1]    # 9
        ])
        for i in range(len(inputs)):
            bits: list[Bit] = Conversion.int64_to_bit_list(inputs[i])
            expected: list[Bit] = expecteds[i]
            self.assertEqual(bits, expected)

    def test_int16_to_bit_list(self) -> None:
        inputs: list[Int16] = cast(list[Int16], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        expecteds: list[list[Bit]] = cast(list[list[Bit]], [
            [0] * 16,                           # 0
            [0] * 15 + [1],                     # 1
            [0] * 14 + [1] + [0],               # 2
            [0] * 14 + [1] + [1],               # 3
            [0] * 13 + [1] + [0] + [0],         # 4
            [0] * 13 + [1] + [0] + [1],         # 5
            [0] * 13 + [1] + [1] + [0],         # 6
            [0] * 13 + [1] + [1] + [1],         # 7
            [0] * 12 + [1] + [0] + [0] + [0],   # 8
            [0] * 12 + [1] + [0] + [0] + [1]    # 9
        ])
        for i in range(len(inputs)):
            bits: list[Bit] = Conversion.int16_to_bit_list(inputs[i])
            expected: list[Bit] = expecteds[i]
            self.assertEqual(bits, expected)

    def test_bit_list_to_int64(self):
        inputs: list[list[Bit]] = cast(list[list[Bit]], [
            [0] * 64,                           # 0
            [0] * 63 + [1],                     # 1
            [0] * 62 + [1] + [0],               # 2
            [0] * 62 + [1] + [1],               # 3
            [0] * 61 + [1] + [0] + [0],         # 4
            [0] * 61 + [1] + [0] + [1],         # 5
            [0] * 61 + [1] + [1] + [0],         # 6
            [0] * 61 + [1] + [1] + [1],         # 7
            [0] * 60 + [1] + [0] + [0] + [0],   # 8
            [0] * 60 + [1] + [0] + [0] + [1]    # 9
        ])
        expecteds: list[Int64] = cast(list[Int64], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        for i in range(len(inputs)):
            value: Int64 = Conversion.bit_list_to_int64(inputs[i])
            expected: Int64 = expecteds[i]
            self.assertEqual(value, expected)

    def test_bit_list_to_int16(self):
        inputs: list[list[Bit]] = cast(list[list[Bit]], [
            [0] * 16,                           # 0
            [0] * 15 + [1],                     # 1
            [0] * 14 + [1] + [0],               # 2
            [0] * 14 + [1] + [1],               # 3
            [0] * 13 + [1] + [0] + [0],         # 4
            [0] * 13 + [1] + [0] + [1],         # 5
            [0] * 13 + [1] + [1] + [0],         # 6
            [0] * 13 + [1] + [1] + [1],         # 7
            [0] * 12 + [1] + [0] + [0] + [0],   # 8
            [0] * 12 + [1] + [0] + [0] + [1]    # 9
        ])
        expecteds: list[Int16] = cast(list[Int16], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        for i in range(len(inputs)):
            value: Int16 = Conversion.bit_list_to_int16(inputs[i])
            expected: Int16 = expecteds[i]
            self.assertEqual(value, expected)

    def test_bytes_to_bit_list(self):
        s: str = "abc"

        bits: list[Bit] = Conversion.bytes_to_bit_list(s.encode("ascii"))
        a_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 0, 1])
        b_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 1, 0])
        c_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 1, 1])
        expected: list[Bit] = a_bits + b_bits + c_bits
        self.assertEqual(bits, expected)

    def test_bit_list_to_bytes(self):
        a_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 0, 1])
        b_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 1, 0])
        c_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 1, 1])
        input_bits: list[Bit] = a_bits + b_bits + c_bits
        expected_str: str = "abc"
        expected_bits: bytes = expected_str.encode("ascii")
        self.assertEqual(Conversion.bit_list_to_bytes(input_bits), expected_bits)
        self.assertEqual(expected_bits.decode("ascii"), expected_str)

    def test_unquote(self):
        s: str = '"abc"'
        self.assertEqual(Conversion.unquote(s), "abc")
        s: str = "abc"
        self.assertEqual(Conversion.unquote(s), "abc")
        s: str = "abc\""
        self.assertEqual(Conversion.unquote(s), "abc")
        s: str = '""abc""'
        self.assertEqual(Conversion.unquote(s), "abc")

    def test_unquote_list(self):
        l: list[str] = ['"abc"', 'abc', 'abc"']
        expected: list[str] = ['abc', 'abc', 'abc']
        self.assertEqual(Conversion.unquote_list(l), expected)
        l: list[str] = ['abc', 'abc"']
        expected: list[str] = ['abc', 'abc']
        self.assertEqual(Conversion.unquote_list(l), expected)
        l: list[str] = ['""abc""', '""abc""', '""abc""']
        expected: list[str] = ['abc', 'abc', 'abc']
        self.assertEqual(Conversion.unquote_list(l), expected)


if __name__ == '__main__':
    unittest.main()