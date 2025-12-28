from collections import Counter
from .sentence import Sentence

def search(text: str, candidates: list[list[str]]) -> list[list[str]]:
    results: list[list[str]] = []
    sentence = Sentence(text.lower())
    words: list[str] = sentence.get_words()

    for candidate in candidates:
        c = [term.lower() for term in candidate]
        if all(term in words for term in c):
            results.append(candidate)
    return results

def find_position(haystack: list[list[str]], needle: list[str]) -> int:
    counter_needle = Counter(needle)
    for idx, sublist in enumerate(haystack):
        if Counter(sublist) == counter_needle:
            return idx
    return -1

