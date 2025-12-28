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
        inputs: list[list[Union[str, str, str, Bit]]] = [
            ['V1', "hash1", "md4", cast(Bit, 0)],
            ['V2', "hash2", "md5", cast(Bit, 1)],
            ['V3', "hash3", "sha224", cast(Bit, 0)],
        ]
        db_path = os.path.abspath(os.path.join(CURRENT_DIR, 'db.sqlite3'))

        with SteganoDb(db_path) as file_db:
            for i in range(len(inputs)):
                v: list[Union[str, str, str, Bit]] = inputs[i]
                file_db.add_section(i, v[0], v[1], v[2], v[3])

            self.assertEqual(len(file_db), len(inputs))
            for i in range(len(inputs)):
                section: Section = file_db.get_section_by_position(i)
                self.assertEqual(section.position, i)
                self.assertEqual(section.section, inputs[i][0])
                self.assertEqual(section.hash_value, inputs[i][1])
                self.assertEqual(section.hash_type, inputs[i][2])
                self.assertEqual(section.bit, inputs[i][3])

            position: int = 0
            for section in file_db.get_sections():
                self.assertEqual(section.position, position)
                self.assertEqual(section.section, inputs[position][0])
                self.assertEqual(section.hash_value, inputs[position][1])
                self.assertEqual(section.hash_type, inputs[position][2])
                self.assertEqual(section.bit, inputs[position][3])
                position += 1

if __name__ == '__main__':
    unittest.main()
