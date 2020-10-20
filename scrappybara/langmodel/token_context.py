class TokenContext(object):
    """Token with surrounding tokens"""

    def __init__(self, token, tokens_before, tokens_after):
        self.token = token
        self.__tokens_before = tokens_before
        self.__tokens_after = tokens_after

    @staticmethod
    def __slide_window(items, window_size):
        return iter(zip(*[items[i:] for i in range(window_size)]))

    @property
    def left_ngram(self):
        return self.__tokens_before + [self.token]

    @property
    def right_ngram(self):
        return [self.token] + self.__tokens_after

    def candidates(self, order):
        """Given an order n, returns all combinations of ngram: before/token/after"""
        assert order > 1
        exploring_range = order - 1
        tokens_before = self.__tokens_before[len(self.__tokens_before) - exploring_range:]
        tokens_after = self.__tokens_after[:exploring_range]
        tokens = tokens_before + [self.token] + tokens_after
        return [' '.join(items) for items in self.__slide_window(tokens, order)]
