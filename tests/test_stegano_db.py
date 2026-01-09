# Usage:
#    python3 -m unittest -v test_stegano_db.py

from typing import Union, cast, Optional
import unittest
import os
import sys

# Set the Python search path...
CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.stegano_db import SteganoDb, Section, Bit

class TestSteganoDb(unittest.TestCase):

    def test_db(self):
        inputs: list[list[Union[str, Bit, str, str, bytes]]] = [
            ['V1', cast(Bit, 0), "TV1", "md5", "abc".encode("utf-8")],
            ['V2', cast(Bit, 1), "TV2", "sha256", "def".encode("utf-8")],
            ['V3', cast(Bit, 1), "TV3", "sha128", "ghi".encode("utf-8")],
        ]
        db_path = os.path.abspath(os.path.join(CURRENT_DIR, 'db.sqlite3'))

        with SteganoDb(db_path) as file_db:
            for i in range(len(inputs)):
                v: list[Union[str, Bit, str, str]] = inputs[i]
                file_db.add_original_text(i, v[0])
                file_db.set_expected_bit(i, v[1])
                file_db.set_traduction(i, v[2], v[3], v[4])

            self.assertEqual(len(file_db), len(inputs))
            for i in range(len(inputs)):
                section: Section = file_db.get_section_by_position(i)
                self.assertEqual(section.position, i)
                self.assertEqual(section.original_text, inputs[i][0])
                self.assertEqual(section.expected_bit, inputs[i][1])
                self.assertEqual(section.traduction, inputs[i][2])
                self.assertEqual(section.algo, inputs[i][3])
                self.assertEqual(section.hash, inputs[i][4].hex())

            position: int = 0
            for section in file_db.get_sections():
                self.assertEqual(section.position, position)
                self.assertEqual(section.original_text, inputs[position][0])
                self.assertEqual(section.expected_bit, inputs[position][1])
                self.assertEqual(section.traduction, inputs[position][2])
                self.assertEqual(section.algo, inputs[position][3])
                self.assertEqual(section.hash, inputs[position][4].hex())
                position += 1

if __name__ == '__main__':
    unittest.main()
