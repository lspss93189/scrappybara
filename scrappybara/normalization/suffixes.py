import enum


@enum.unique
class Suffix(enum.IntEnum):
    """Suffixes detected by lemmatization"""

    # Verbs
    # -------------------------------------------------------------------------->

    THIRD_PERSON = 1
    PAST = 2  # Preterit or past participle
    PROGRESSIVE = 3

    # Nouns
    # -------------------------------------------------------------------------->

    PLURAL = 4

    # Adjectives
    # -------------------------------------------------------------------------->

    COMPARATIVE = 5
    SUPERLATIVE = 6
