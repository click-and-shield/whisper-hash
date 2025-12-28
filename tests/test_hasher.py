# Usage:
# python3 -m unittest -v test_hasher.py

import unittest
import os
import sys

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.hasher import Hasher, ALGORITHMS

class TestDiskList(unittest.TestCase):

    def test_hash(self):
        for algorithm in ALGORITHMS:
            print('%s - %d' % (Hasher(algorithm).hash('abc'), Hasher(algorithm).get_parity('abc')))

if __name__ == '__main__':
    unittest.main()
