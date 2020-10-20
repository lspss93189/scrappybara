import enum


@enum.unique
class Trans(enum.IntEnum):
    """Arc-eager projective parsing"""

    LEFT = 0  # Left arc + reduce
    RIGHT = 1  # Right arc + shift
    REDUCE = 2  # Pop stack
    SHIFT = 3  # Push token from buffer to stack
