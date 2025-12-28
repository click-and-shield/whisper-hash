# Usage:
# python3 -m unittest -v test_disk_list.py

import unittest
import os
import sys

# Set the Python search path...
CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.disk_list import DiskList

class TestDiskList(unittest.TestCase):

    def test_list(self):
        inputs: list[str] = ['e1', 'e2', 'e3']
        dl = DiskList()
        for e in inputs:
            dl.append(e)
        self.assertEqual(len(dl), len(inputs))
        for i in range(len(dl)):
            self.assertEqual(dl[i], inputs[i])
        dl.destroy()

    def test_list_set(self):
        inputs: list[str] = ['e1', 'e2', 'e3']
        replacements: list[str] = ['r1', 'r2', 'r3']
        dl = DiskList()
        for e in inputs:
            dl.append(e)
        for i in range(len(inputs)):
            dl[i] = replacements[i]
        for i in range(len(dl)):
            self.assertEqual(dl[i], replacements[i])
        dl.destroy()

if __name__ == '__main__':
    unittest.main()
