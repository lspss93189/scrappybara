import enum


@enum.unique
class Tag(enum.IntEnum):
    """Part-of-speech tags.
    To avoid confusion, code names are different from dependency names (except for PAD).
    """

    # THROW
    # -------------------------------------------------------------------------->

    PAD = 0  # Batch padding (0's)

    # TAGSET
    # -------------------------------------------------------------------------->

    ADJ = 1  # Adjective
    PREP = 2  # Preposition
    ADV = 3  # Adverb
    MAT = 4  # Auxiliary or modal that indicates the [M]ood, [A]spect or [T]ense of a verb
    CONJ = 5  # Conjunction (subordinative or coordinative)
    DET = 6  # Determiner
    EXPR = 7  # Expressions and interjections
    NOUN = 8  # Noun
    NUM = 9  # Numeral
    FRAG = 10  # Fragment of a verb (equivalent to particle "PART" dependency)
    PRON = 11  # Pronoun
    PROPN = 12  # Proper noun
    PUNCT = 13  # Punctuation
    VERB = 14  # Verb
    SYM = 15  # Symbol (URLs, hash tags, @, emojis, special signs)
    THERE = 16  # Existential "there"/"here"


NB_TAGS = len([tag for tag in Tag])

NOUN_TAGS = {Tag.NOUN, Tag.PROPN, Tag.PRON, Tag.SYM, Tag.NUM}
PROP_TAGS = NOUN_TAGS | {Tag.ADJ}
LEX_TAGS = {Tag.NOUN, Tag.PROPN, Tag.ADJ, Tag.VERB}  # Tags for lexemes
