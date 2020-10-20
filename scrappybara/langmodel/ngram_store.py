from scrappybara.langmodel.ngram import Ngram


class NgramStore(object):
    """Maintains ngram counts"""

    def __init__(self):
        self.__store = {}  # text => Ngram

    def __len__(self):
        return len(self.__store)

    @property
    def ngrams(self):
        return self.__store.values()

    def make_ngram(self, text):
        """Returns existing ngram or make a new one"""
        if text in self.__store:
            ngram = self.__store[text]
            ngram.count += 1
            return ngram
        ngram = Ngram(text)
        self.__store[text] = ngram
        return ngram
