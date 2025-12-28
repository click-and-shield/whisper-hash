from typing import Set
import hashlib

ALGORITHMS: Set[str] = {'md5', 'sha224', 'sha256', 'sha384', 'sha512', 'sha512_224', 'sha512_256', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'}

class Hasher:

    def __init__(self, algorithm: str):
        if algorithm not in ALGORITHMS:
            raise ValueError(f'Algorithm "{algorithm}" is not supported (supported algorithms: {ALGORITHMS}).')
        self.algorithm: str = algorithm

    def hash(self, data: str) -> str:
        return hashlib.new(self.algorithm, data.encode()).hexdigest()[:32]

    def get_parity(self, data: str):
        h = self.hash(data)
        return sum(ord(c) for c in h) % 2
