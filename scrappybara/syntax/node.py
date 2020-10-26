from scrappybara.syntax.tags import Tag


class Node(object):
    """Belongs to a parse tree"""

    def __init__(self, idx, text, tag):
        self.idx = idx  # 0-index of token in tokenized sentence
        self.text = text  # as found in the original text: case sensitive
        self.tag = tag  # part-of-speech tag
        # STANDARDIZATION
        self.standard = text.lower()
        # NODIFICATION
        self.particles = []  # verb/adj particles (lower case)
        self.det = None  # series of determiners attached to the noun, chunked string
        self.is_inf_to = False  # verb with form "TO + infinitive"
        # CHUNKING
        self.chunk = None  # string, noun phrase
        # LEMMATIZATION
        self.lemma = None
        self.suffix = None
        # CANONICALIZATION
        self.canon = None  # canonical representation
        self.active_verb = None  # active verb from past participle
        # RESOURCE LINKING
        self.resource = None

    def __str__(self):
        return self.canon

    def __repr__(self):
        return self.canon

    @property
    def is_lexeme(self):
        """Whether node is part of vocabulary"""
        return self.tag in {Tag.NOUN, Tag.PROPN, Tag.ADJ, Tag.VERB}
