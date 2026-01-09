# Usage:
# python3 -m unittest -v test_hasher.py

from typing import Optional
import unittest
import os
import sys

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.hasher import Hasher, KEY_LENGTH, ALGORITHMS

class TestDiskList(unittest.TestCase):

    def test_hasher(self):
        texts: list[str] = ['a'*i for i in range(1, KEY_LENGTH+3)]
        password: str = 'password'
        hasher: Hasher = Hasher(password, verbose=True)

        print('\nKEY_LENGTH = {}'.format(KEY_LENGTH))
        print('ALGO COUNT   = {}'.format(len(ALGORITHMS)))

        counter: int = 0
        last_hash: Optional[bytes] = None
        for text in texts:
            print('%-3d: ' % counter, end='')
            algo: str = hasher.next_hash_algorithm(last_hash)
            h, p = hasher.get_parity(algo, text)
            last_hash = h
            self.assertTrue(p == 0 or p == 1)
            self.assertEqual(len(h), KEY_LENGTH)
            counter += 1

if __name__ == '__main__':
    unittest.main()
