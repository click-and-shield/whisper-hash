from typing import Tuple
import hashlib
from .params import KEY_LENGTH
from argon2.low_level import hash_secret_raw, Type

ALGORITHMS: list[str] = ['md5', 'sha224', 'sha256', 'sha384', 'sha512', 'sha512_224', 'sha512_256', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512']

def xor_bytes(a: bytes, b: bytes) -> bytes:
    if len(a) != len(b):
        raise ValueError("The 2 lists of bytes must have the same length ({} vs {}).".format(len(a), len(b)))
    return bytes(x ^ y for x, y in zip(a, b))

class Hasher:

    def __init__(self, secret_key: str, verbose: bool = False):
        # Generate 32 bytes long key from the password.
        # Please note that we are not using a salt here.
        self.key: bytes = hash_secret_raw(
            secret=secret_key.encode(),
            salt=bytes(1024),
            time_cost=3,
            memory_cost=65536,
            parallelism=1,
            hash_len=KEY_LENGTH,
            type=Type.ID
        )
        self.hash_algorithm_index: int = 0
        self.last_hash: bytes = bytes(KEY_LENGTH)
        self.verbose: bool = verbose

    def update(self) -> None:
        self.key = xor_bytes(self.key, self.last_hash)
        self.hash_algorithm_index = 0

    def next_hash_algorithm(self) -> str:
        if self.hash_algorithm_index >= KEY_LENGTH:
            self.update()
        i: int = self.key[self.hash_algorithm_index] % len(ALGORITHMS)
        self.hash_algorithm_index += 1
        return ALGORITHMS[i]

    def hash(self, algo: str, data: str) -> Tuple[str, bytes]:
        h: bytes = hashlib.new(algo, data.encode()).digest()
        key: bytes = hash_secret_raw(
            secret=h,
            salt=bytes(1024),
            time_cost=3,
            memory_cost=65536,
            parallelism=1,
            hash_len=KEY_LENGTH,
            type=Type.ID
        )
        self.last_hash = key
        return algo, key

    def get_parity(self, algo: str, data: str) -> Tuple[bytes, int]:
        algo, h = self.hash(algo, data)
        p: int = sum(c for c in h) % 2
        if self.verbose:
            print('%-10s: %s %s -> %d' %(algo, h.hex(), self.key.hex(), p))
        return h, p

