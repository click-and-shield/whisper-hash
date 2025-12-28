from typing import Tuple, Optional, cast, Literal
from typing import Generator
from .types import Char

class SectionDetector:

    def __init__(self) -> None:
        self.section: str = ''
        self.previous_is_nl: bool = False

    def detect(self, character: Optional[Char], last: bool = False) -> Tuple[bool, Optional[str]]:
        if last:
            if self.section == '':
                return False, None
            return True, self.section
        if character == '\n':
            if self.previous_is_nl:
                return False, None
            self.previous_is_nl = True
            if self.section == '':
                return False, None
            section: str = self.section
            self.section = ''
            return True, section
        self.previous_is_nl = False
        self.section += cast(str, character)
        return False, None

def read_sections_from_file(path: str) -> Generator[str, None, None]:
    detector = SectionDetector()
    with open(path, 'r') as f:
        while True:
            character: str = f.read(1)
            if character == '': # the end of the file as been reached
                found, section = detector.detect(character=None, last=True)
                if found:
                    yield section
                return
            found, section = detector.detect(character=cast(Char, character))
            if found:
                yield section
