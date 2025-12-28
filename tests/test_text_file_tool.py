# Usage:
# python3 -u -m unittest -v test_text_file_tool.py

import unittest
import os
import sys
import tempfile

# Set the Python search path...
CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
INPUT_PATH: str = os.path.join(tempfile.gettempdir(), 'needle.txt')
sys.path.insert(0, SEARCH_PATH)

from whisper import text_file_tool


def set_input_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)

class TestFileTool(unittest.TestCase):

    def test_read_sections_from_file_1(self):
        inputs = ['Sentence1 is first.',
                  '',
                  'Is sentence2 second ?',
                  '',
                  'Sentence3 is next ...',
                  '',
                  "Test's is processed.",
                  '',
                  'This is a unit-test.',
                  '']
        set_input_file(INPUT_PATH, "\n".join(inputs))
        sections: list[str] = []
        for section in text_file_tool.read_sections_from_file(INPUT_PATH):
            sections.append(section)
        self.assertEqual(len(sections), int(len(inputs) / 2))
        for i in range(len(sections)):
            self.assertEqual(sections[i], inputs[i*2].strip(' '))

    def test_read_sections_from_file_2(self):
        inputs = ['Sentence1 is first.',
                  '',
                  '',
                  'Is sentence2 second ?',
                  '',
                  '',
                  'Sentence3 is next ...',
                  '',
                  '',
                  "Test's is processed.",
                  '',
                  '',
                  'This is a unit-test.',
                  '',
                  '']
        set_input_file(INPUT_PATH, "\n".join(inputs))
        sections: list[str] = []
        for section in text_file_tool.read_sections_from_file(INPUT_PATH):
            sections.append(section)
        self.assertEqual(len(sections), int(len(inputs) / 3))
        for i in range(len(sections)):
            self.assertEqual(sections[i], inputs[i*3].strip(' '))

    def test_read_lines_from_file_3(self):
        inputs = ['Sentence1.']
        set_input_file(INPUT_PATH, ''.join(inputs))
        sections: list[str] = []
        for section in text_file_tool.read_sections_from_file(INPUT_PATH):
            sections.append(section)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], 'Sentence1.')

    def test_read_lines_from_file_4(self):
        inputs = ['', 'Sentence1.']
        set_input_file(INPUT_PATH, '\n'.join(inputs))
        sections: list[str] = []
        for section in text_file_tool.read_sections_from_file(INPUT_PATH):
            sections.append(section)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], 'Sentence1.')

    def test_read_lines_from_file_5(self):
        inputs = ['', '', 'Sentence1.']
        set_input_file(INPUT_PATH, '\n'.join(inputs))
        sections: list[str] = []
        for section in text_file_tool.read_sections_from_file(INPUT_PATH):
            sections.append(section)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], 'Sentence1.')

if __name__ == '__main__':
    unittest.main()
