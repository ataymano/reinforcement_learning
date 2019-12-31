from enum import Enum


class Features(Enum):
    CONTEXT = 1,
    ACTION = 2,
    SLOT = 3


class Problem(Enum):
    CB = 1,
    CCB = 2
