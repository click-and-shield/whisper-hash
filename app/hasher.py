import argparse
import sys
import os

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
print("Set search path: {}".format(SEARCH_PATH))
sys.path.insert(0, SEARCH_PATH)

from whisper.hasher import Hasher


# Parse the command line arguments
parser = argparse.ArgumentParser(description='Hide a text file within a generated text file.')
parser.add_argument('input',
                    type=str,
                    help='path to input file')
parser.add_argument('algo',
                    type=str,
                    help='name of the hashing algorithm to use')

args = parser.parse_args()
input_path: str = args.input
algo: str = args.algo

with open(input_path, "r") as f:
    content = f.read()

hasher = Hasher(algo)
h, bit = hasher.get_parity(algo, content)
print("hash: {}".format(h.hex()))
print("bit:  {}\n".format(bit))

