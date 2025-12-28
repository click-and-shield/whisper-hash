# Usage:
# python3 -m unittest -v test_prompt_builder.py

import unittest
import os
import sys

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

TPL: str = """
V1: {__V1__}
V2: {__V2__}
V3: {__V3__}
"""

from whisper.prompt_builder import PromptBuilder

class TestPrompt(unittest.TestCase):

    def test_prompt_1(self):
        prompt: PromptBuilder = PromptBuilder(TPL)
        p: str = prompt.generate_prompt({'__V1__': '1', '__V2__': '2', '__V3__': '3'})
        self.assertEqual(
            p,
            "\nV1: 1\nV2: 2\nV3: 3\n"
        )

if __name__ == '__main__':
    unittest.main()
