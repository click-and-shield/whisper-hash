from typing import Tuple
import itertools
from .config import Config
from .types import Bit
from .list_tools import shuffle

class Context:

    @staticmethod
    def generate_combinations(lists_of_lists_of_terms: list[list[str]]) -> list[list[str]]:
        """Generate all possible combinations of the given lists."""
        l: list[list[str]] = [list(t) for t in itertools.product(*lists_of_lists_of_terms)]
        for i in range(len(l)):
            l[i].sort()
        return l

    @staticmethod
    def generate_all_terms(cover_words: list[list[str]]) -> list[str]:
        all_terms: list[str] = []
        for terms in cover_words:
            all_terms.extend(terms)
        all_terms.sort()
        return all_terms

    def __init__(self, config: Config):
        self.combinations: list[list[str]] = Context.generate_combinations(config.cover_words)
        self.all_terms: list[str] = Context.generate_all_terms(config.cover_words)
        self.count_combinations: int = len(self.combinations)
        self.index_0: int = 0 # used if the bit to cover is 0
        self.index_1: int = 1 # used if the bit to cover is 1

    def shuffle(self):
        """Shuffle the combinations of cover words.
        Please note that in order to make the unit tests deterministic, the combinations are not automatically shuffled.
        """
        self.combinations: list[list[str]] = shuffle(self.combinations)

    def get_combination(self, combinations: list[list[str]], idx: int, quoted: bool = False) -> Tuple[list[str], list[str]]:
        c: list[str] = combinations[idx]
        t: list[str] = [x for x in self.all_terms if x not in c]
        if quoted:
            for i in range(len(c)):
                c[i] = f'"{c[i]}"'
            for i in range(len(t)):
                t[i] = f'"{t[i]}"'
        return c, t

    def get_next_combination(self, bit: Bit, quoted: bool=False) -> Tuple[list[str], list[str]]:
        idx: int = self.index_0 if bit == 0 else self.index_1
        c, t = self.get_combination(self.combinations, idx, quoted)
        if bit == 0:
            self.index_0 = (self.index_0 + 2) % self.count_combinations
        else:
            self.index_1 = (self.index_1 + 2) % self.count_combinations
        return c, t

