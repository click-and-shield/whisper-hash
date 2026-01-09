# Usage:
#   python -u reveal.py --verbose secret-key ../test-data/output.txt message.txt

import argparse
import sys
import os
from pathlib import Path

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.whisperer import Revealer, Config

def get_script_dir() -> Path:
    """Returns the path to the directory containing the script."""
    return Path(__file__).resolve().parent

if __name__ == '__main__':
    script_dir: Path = get_script_dir()

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Reveal a text file hidden within another text file')
    parser.add_argument('--verbose',
                        dest='verbose_flag',
                        action='store_true',
                        help='activate verbose output')
    parser.add_argument('secret_key',
                        type=str,
                        help='the secret key used to hide the text file')
    parser.add_argument('murmur',
                        type=str,
                        help='path to the text file used as hiding place')
    parser.add_argument('output',
                        type=str,
                        help='path to the output file')

    args = parser.parse_args()
    verbose_flag: bool = args.verbose_flag
    secret_key: str = args.secret_key
    murmur_path: str = args.murmur
    output_path: str = args.output

    if verbose_flag:
        print('murmur:     "{}"'.format(murmur_path))
        print('output:     "{}"'.format(output_path))
        print('secret key: "{}"\n'.format(secret_key))

    revealer = Revealer(murmur_path, output_path, secret_key, verbose_flag)
    revealer.reveal()


