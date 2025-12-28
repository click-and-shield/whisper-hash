import random
import string


class RandTools:

    @staticmethod
    def random_string(length: int) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
