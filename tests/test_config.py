# Usage:
# python3 -m unittest -v test_config.py

import unittest
import sys
import os
import tempfile

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
INPUT_PATH: str = os.path.join(tempfile.gettempdir(), 'config.yaml')
sys.path.insert(0, SEARCH_PATH)

from whisper.config import Config, load_config

def set_input_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)

class TestConfig(unittest.TestCase):

    def test_config1(self):
        input_text = """
        model: gpt-3.5-turbo
        temperature: 0.7
        top_p: 0.9
        system:
            first_request: "first request"
            next_requests: "next request"
        assistant: null
        user: |
            {TEXT}
        """
        try:
            set_input_file(INPUT_PATH, input_text)
            config: Config = load_config(INPUT_PATH)

            self.assertEqual(config.model, "gpt-3.5-turbo")
            self.assertEqual(config.temperature, 0.7)
            self.assertEqual(config.top_p, 0.9)
            self.assertEqual(config.assistant, None)
            self.assertEqual(config.user, "{TEXT}")
        finally:
            if os.path.exists(INPUT_PATH):
                os.remove(INPUT_PATH)

    def test_config2(self):
        input_text = """
        temperature: 0.7
        top_p: 0.9
        system:
            first_request: "first request"
            next_requests: "next request"
        assistant: null
        user: |
            {TEXT}
        """
        try:
            set_input_file(INPUT_PATH, input_text)
            self.assertRaises(ValueError, load_config, INPUT_PATH)
        finally:
            if os.path.exists(INPUT_PATH):
                os.remove(INPUT_PATH)

    def test_config3(self):
        input_text = """
        model: gpt-3.5-turbo
        temperature: toto
        top_p: 0.9
        system:
            first_request: "first request"
            next_requests: "next request"
        assistant: null
        user: |
            {TEXT}
        """
        try:
            set_input_file(INPUT_PATH, input_text)
            self.assertRaises(ValueError, load_config, INPUT_PATH)
        finally:
            if os.path.exists(INPUT_PATH):
                os.remove(INPUT_PATH)

    def test_config4(self):
        input_text = """
        model: gpt-3.5-turbo
        temperature: 0.7
        top_p: 0.9
        system:
            first_request: "first request"
            next_requests: "next request"
        assistant: ok
        user: |
            {TEXT}
        """
        try:
            set_input_file(INPUT_PATH, input_text)
            config: Config = load_config(INPUT_PATH)

            self.assertEqual(config.model, "gpt-3.5-turbo")
            self.assertEqual(config.temperature, 0.7)
            self.assertEqual(config.top_p, 0.9)
            self.assertEqual(config.assistant, "ok")
            self.assertEqual(config.user, "{TEXT}")
        finally:
            if os.path.exists(INPUT_PATH):
                os.remove(INPUT_PATH)

if __name__ == '__main__':
    unittest.main()

