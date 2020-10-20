from scrappybara.utils.text import CONSONANTS, VOWELS


class Inflector(object):

    def __init__(self, language_model, lemma_pp):
        self.__lm = language_model
        self.__lemma_pp = lemma_pp

    def past_participle(self, lemma):
        try:
            # Irregular
            return self.__lemma_pp[lemma]
        except KeyError:
            # Special endings
            if len(lemma) > 2:
                if lemma[-3] in CONSONANTS and lemma.endswith('ie'):
                    return lemma + 'd'
            if len(lemma) > 1:
                if lemma[-2] in CONSONANTS and lemma[-1] == 'y':
                    return lemma[:-1] + 'ied'
                if lemma[-2] in CONSONANTS and lemma.endswith('e'):
                    return lemma + 'd'
                if lemma[-2] in VOWELS and lemma[-1] in CONSONANTS:
                    best = self.__lm.best_token(lemma + 'ed', lemma + lemma[-1] + 'ed')
                    if best:
                        return best
            # Standard case
            return lemma + 'ed'
