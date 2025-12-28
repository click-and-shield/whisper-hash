# Usage:
#   python -m unittest test_context.py

import tempfile
import unittest
import sys
import os
from typing import cast


CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
INPUT_PATH: str = os.path.join(tempfile.gettempdir(), 'needle.txt')
sys.path.insert(0, SEARCH_PATH)

from whisper.config import load_config, Config
from whisper.context import Context
from whisper.types import Bit

def set_input_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)

CONFIG: str = '''
first-lines: Botanical report.
request:
  # Parameters for constructing the LLM request to generate a data-masking sentence.
  # Note: The filler sentence uses terms specified by the "key-hide" keys defined below.
  system: "A"
  assistant: "B"
  user: "C"
  first_user: "D"
  last_user: "E"
cover-words:
  # These keys specify the terms used to embed data within the generated cover medium.
  - [A1, B1]
  - [C1, D1]
  - [E1, F1]
'''

class TestContext(unittest.TestCase):

    def test_context(self):
        try:
            set_input_file(INPUT_PATH, CONFIG)
            config: Config = load_config(INPUT_PATH)
            ctx: Context = Context(config)

            expected_all_terms: list[str] = ['a1', 'b1', 'c1', 'd1', 'e1', 'f1']
            expected_all_terms.sort()
            self.assertEqual(ctx.all_terms, expected_all_terms)

            expected_hide: list[list[str]] = [['a1', 'c1', 'e1'], ['a1', 'c1', 'f1'], ['a1', 'd1', 'e1'], ['a1', 'd1', 'f1'], ['b1', 'c1', 'e1'], ['b1', 'c1', 'f1'], ['b1', 'd1', 'e1'], ['b1', 'd1', 'f1']]
            self.assertEqual(ctx.combinations, expected_hide)

            self.assertEqual(ctx.index_0, 0)
            self.assertEqual(ctx.index_1, 1)

            # Test the getter for the combinations used to hide - bit 0
            c, t = ctx.get_next_combination(cast(Bit, 0))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[0])
            self.assertEqual(set(t), expected_t)

            c, t = ctx.get_next_combination(cast(Bit, 0))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[2])
            self.assertEqual(set(t), expected_t)

            c, t = ctx.get_next_combination(cast(Bit, 0))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[4])
            self.assertEqual(set(t), expected_t)

            c, t = ctx.get_next_combination(cast(Bit, 0))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[6])
            self.assertEqual(set(t), expected_t)

            c, t = ctx.get_next_combination(cast(Bit, 0))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[0])
            self.assertEqual(set(t), expected_t)

            # Test the getter for the combinations used to hide - bit 1
            c, t = ctx.get_next_combination(cast(Bit, 1))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[1])
            self.assertEqual(set(t), expected_t)

            c, t = ctx.get_next_combination(cast(Bit, 1))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[3])
            self.assertEqual(set(t), expected_t)

            c, t = ctx.get_next_combination(cast(Bit, 1))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[5])
            self.assertEqual(set(t), expected_t)

            c, t = ctx.get_next_combination(cast(Bit, 1))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[7])
            self.assertEqual(set(t), expected_t)

            c, t = ctx.get_next_combination(cast(Bit, 1))
            expected_t = set(expected_all_terms) - set(c)
            self.assertEqual(c, expected_hide[1])
            self.assertEqual(set(t), expected_t)

        finally:
            if os.path.exists(INPUT_PATH):
                os.remove(INPUT_PATH)
