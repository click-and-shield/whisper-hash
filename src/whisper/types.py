from enum import Enum
from typing import NewType, TypeVar

Bit = NewType('Bit', int) # a bit is either 0 or 1
Int64 = NewType('Int64', int)
Int16 = NewType('Int16', int)
Char = NewType('Char', str)
Vector = list[Bit]
T = TypeVar("T")

class MessageType(Enum):
    SYSTEM = "SYSTEM"
    ASSISTANT = "ASSISTANT"
    USER = "USER"
    USER_INIT = "USER_INIT"
    USER_TERMINAL = "USER_TERMINAL"

class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
