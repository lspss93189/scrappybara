class Node(object):
    """Belongs to a parse tree"""

    def __init__(self, idx, text, standard, tag):
        self.idx = idx  # 0-index of token in tokenized sentence
        self.text = text  # as found in the original text: case sensitive
        self.standard = standard  # standardized text: case insensitive, standard orthography
        self.tag = tag  # part-of-speech tag
        # NODIFICATION
        self.particles = []  # verb/adj particles (lower case)
        self.det = None  # series of determiners attached to the noun, chunked string
        self.is_inf_to = False  # verb with form "TO + infinitive"
        # LEMMATIZATION
        self.lemma = standard
        self.suffix = None
        # CANONICALIZATION
        self.canon = standard  # canonical representation
        self.active_verb = None  # active verb from past participle
        # ENTITY LINKING
        self.entity = None  # Entity object

    def __str__(self):
        return self.canon

    def __repr__(self):
        return self.canon
