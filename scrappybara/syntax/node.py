from scrappybara.syntax.tags import Tag


class Node(object):
    """Belongs to a parse tree"""

    def __init__(self, token_idx, text, tag):
        self.idx = token_idx  # 0-index of the token in a sentence
        self.original = text  # As found in text
        self.standard = text.lower()  # Flat word
        self.tag = tag
        # NODIFICATION
        self.particles = []  # Verb/adj particles (lower case)
        self.det = None  # Series of determiners attached to the noun, chunked string
        self.is_inf_to = False  # Verb with form "TO + infinitive"
        # LEMMATIZATION
        self.lemma = self.standard
        self.suffix = None
        # CHUNKING
        self.chunk = None  # Common nouns chunked into a single string
        # CANONICALIZATION
        self.canon = self.standard  # Canonical representation
        self.active_verb = None  # Active verb from past participle
        # RESOURCE LINKING
        self.resource = None
        # PATTERNS MATCHING
        self.hypernyms = []
        self.agents_actions = []  # List of tuples (agent, action) attached to a patient

    def __str__(self):
        return self.canon

    def __repr__(self):
        return self.canon

    @property
    def has_art_a(self):
        return self.det in {'a', 'an'}

    @property
    def has_art_the(self):
        return self.det == 'the'

    @property
    def is_lexeme(self):
        """Excludes adverbs, numbers & symbols"""
        return self.tag in {Tag.NOUN, Tag.PROPN, Tag.ADJ, Tag.VERB}
