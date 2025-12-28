import random
from .types import T


def shuffle(liste: list[T], seed: int = 42) -> list[T]:
    """
    Shuffles a list *deterministically* based on a provided seed.

    This function creates a copy of the input list and shuffles it using
    a random number generator initialized with the given seed. The original
    list remains unchanged.

    Args:
        liste (list[T]): The list to be shuffled.
        seed (int, optional): The seed for the random number generator.
            Defaults to 42.

    Returns:
        list[T]: A new list containing the shuffled elements.
    """
    clone = liste.copy()
    rnd = random.Random(seed)
    rnd.shuffle(clone)
    return clone

