import math


def _logp(proba):
    """Log-probability"""
    try:
        return math.log(proba)
    except ValueError:
        return float('-inf')


class Ngram(object):

    def __init__(self, text):
        self.text = text
        self.tokens = text.split()
        self.count = 1
        self.__proba = None
        self.logp = None

    def __str__(self):
        return ' '.join(self.tokens)

    def __repr__(self):
        return ' '.join(self.tokens)

    def __gt__(self, other):
        return self.proba > other.proba  # If 2 ngrams are the same, their probas are the same

    @property
    def proba(self):
        return self.__proba

    @proba.setter
    def proba(self, value):
        self.__proba = value
        self.logp = _logp(value)

    @property
    def order(self):
        return len(self.tokens)

    # Kneser-Ney smoothing
    # -------------------------------------------------------------------------->

    @property
    def last_token(self):
        return self.tokens[-1]

    @property
    def without_last_token(self):
        assert self.order > 1
        return ' '.join(self.tokens[:-1])

    @property
    def wc_last_token(self):
        """Replace last token with wildcard"""
        return ' '.join([self.without_last_token, '•'])

    @property
    def prepend_wc(self):
        """Prepend wildcard"""
        return ' '.join(['•', self.text])

    @property
    def continuous_ngram(self):
        """Continuous ngram for next order: prepend wildcard & replace last token with wildcard"""
        wc_last_token = self.wc_last_token
        return ' '.join(['•', wc_last_token])

    def lower_order(self, order):
        """Truncate beginning of ngram to a target order"""
        assert 0 < order < self.order
        return ' '.join(self.tokens[self.order - order:])
