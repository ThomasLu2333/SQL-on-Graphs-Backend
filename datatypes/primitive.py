from enum import Enum
from typing import Union

INT = int
FLOAT = float
BOOL = bool
STR = str
NULL = None

class PrimitiveTypes(Enum):
    """
    An Enum containing all primitive data types supported by SQLonGraph.
    """
    INT = INT
    FLOAT = FLOAT
    BOOL = BOOL
    STR = STR

Primitive = Union[INT, FLOAT, BOOL, STR, NULL]