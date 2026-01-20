# Usage;
#    python hasher.py secret-key

import argparse
import sys
import os

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
print("Set search path: {}".format(SEARCH_PATH))
sys.path.insert(0, SEARCH_PATH)

from whisper.hasher import Hasher, ALGORITHMS


# Parse the command line arguments
parser = argparse.ArgumentParser(description='Test the Hasher class.')
parser.add_argument('key',
                    type=str,
                    help='the secret key')

args = parser.parse_args()
secret_key: str = args.key

hasher = Hasher(secret_key, verbose=True)
print('{}'.format(hasher.key.hex()))
for i in range(len(hasher.key)):
    p: int = hasher.key[i] % len(ALGORITHMS)
    print('| `%d` | `%x` | `%d` | `%-3d %% %d = %d` | `ALGORITHMS[%2d]`: `%s` |' % (i, hasher.key[i], hasher.key[i], hasher.key[i], len(ALGORITHMS), p, p, ALGORITHMS[p]))
print('\n\n')

hasher.get_parity("md5", "Le lecteur découvre très vite que le temps lui-même est suspect. Les horloges qui sonnent treize heures ou l’indication d’événements quotidiens perturbés donnent le sentiment que la réalité a été modifiée, que les conventions et les repères élémentaires ne sont plus fiables. Ce décalage subtil prépare le terrain à l’angoisse et à l’incertitude qui imprègnent tout le récit.")

