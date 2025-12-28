# Usage:
# python3 -m unittest -v test_message.py

import unittest
import tempfile
import os
import sys

# Set the Python search path...
CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
INPUT_PATH: str = os.path.join(tempfile.gettempdir(), 'needle.txt')
sys.path.insert(0, SEARCH_PATH)

from whisper.message import Message
from whisper import Int64, Bit, Vector
from typing import cast
from whisper.conversion import Conversion

class TestMessage(unittest.TestCase):

    def test_string_to_vector(self):
        input_str: str = "abc"
        length_bits: list[Bit] = Conversion.int64_to_bit_list(cast(Int64, len(input_str)))
        a_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 0, 1])
        b_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 1, 0])
        c_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 1, 1])
        expected: list[Bit] = length_bits + a_bits + b_bits + c_bits
        result: list[Bit] = Message.string_to_vector(input_str)
        self.assertEqual(result, expected)

    def test_load_text_file_as_vector(self):
        input_str: str = "abc"
        with open(INPUT_PATH, 'w') as f:
            f.write(input_str)
        vector: Vector = Message.load_text_file_as_vector(INPUT_PATH)
        length_bits: list[Bit] = Conversion.int64_to_bit_list(cast(Int64, len(input_str)))
        a_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 0, 1])
        b_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 1, 0])
        c_bits: list[Bit] = cast(list[Bit], [0, 1, 1, 0, 0, 0, 1, 1])
        expected: list[Bit] = length_bits + a_bits + b_bits + c_bits
        self.assertEqual(vector, expected)


if __name__ == '__main__':
    unittest.main()
