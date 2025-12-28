# Usage:
#   python -m unittest test_combination.py
from typing import Optional, Tuple, cast
import tempfile
import unittest
import sys
import os

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
INPUT_PATH: str = os.path.join(tempfile.gettempdir(), 'needle.txt')
sys.path.insert(0, SEARCH_PATH)

import whisper.combination


class TestCombination(unittest.TestCase):

    def test_search(self):

        candidates: list[list[str]] = [
            ['ciel', 'bleu', 'nuages'],
            ['ciel', 'vert', 'nuages'],
            ['terre', 'bleu', 'nuages'],
            ['terre', 'voiture', 'table'],
            ['a', 'b', 'c'],
            ['d', 'e', 'f'],
            ['g', 'h', 'i']
        ]

        tests_set: list[Tuple[str, list[list[str]], Optional[list[list[str]]]]] = [
            ("Le ciel est bleu et les nuages sont rouges.",
             candidates, [['ciel', 'bleu', 'nuages']]),
            ("Les nuages sont rouges et le ciel est bleu.",
             candidates, [['ciel', 'bleu', 'nuages']]),
            ("le sous-marin navigue dans l'océan.",
             candidates, []),
            ("La voiture circule sur la terre et transporte une table.",
             candidates, [['terre', 'voiture', 'table']]),
            ("La voiture circule sur la terre et transporte une table (b c a).",
             candidates, [['terre', 'voiture', 'table'], ['a', 'b', 'c']]),
            ("a b c d e f g h i",
             candidates, [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]),
            ("a b c d e f g h i",
             [['a', 'b'], ['c', 'd'], ['e']], [['a', 'b'], ['c', 'd'], ['e']])
        ]

        for text, candidates, expected_combinations in tests_set:
            combinations: list[list[str]] = whisper.combination.search(text, candidates)
            self.assertEqual(combinations, expected_combinations)

    def test_find_position(self):
        combinations: list[list[str]] = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
        combination: list[str] = ['a', 'b', 'c']
        self.assertEqual(whisper.combination.find_position(combinations, combination), 0)
        combinations: list[list[str]] = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
        combination: list[str] = ['b', 'a', 'c']
        self.assertEqual(whisper.combination.find_position(combinations, combination), 0)
        combinations: list[list[str]] = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
        combination: list[str] = ['x', 'x', 'x']
        self.assertEqual(whisper.combination.find_position(combinations, combination), -1)

if __name__ == '__main__':
    unittest.main()

