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
        # LEMMATIZATION
        self.lemma = self.standard
        self.suffix = None
        # CANONICALIZATION
        self.canon = self.lemma  # canonical representation
        self.active_verb = None  # active verb from past participle
        # ENTITY LINKING
        self.entity = None  # Entity object

    def __str__(self):
        return self.canon

    def __repr__(self):
        return self.canon
