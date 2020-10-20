import re


def _split_token(token, middles, endings):
    """Returns start, middle & end of token.
    If searching only for middles, pass the empty string '' in the endings list.
    (and vice versa if searching only for endings)
    """
    pattern = re.compile(r'([a-z]+)(%s)(%s)' % ('|'.join(middles), '|'.join(endings)), re.I)
    match = re.fullmatch(pattern, token)
    if match:
        start, middle, end = match.group(1, 2, 3)
        if len(start) > 1:
            return start, middle, end
    return None


class Standardizer(object):

    def __init__(self, language_model):
        self.__lm = language_model

    def __call__(self, token):
        """Standardizes orthography according to language model"""
        token = token.lower()
        if self.__lm.has_ngram(token, 5):
            return token
        # col-our-ed or col-o-red ?
        start_mid_end = _split_token(token, ['our', 'or'], ['ing', 'ed', 's', ''])
        if start_mid_end is not None:
            start, _, end = start_mid_end
            if len(start) > 2:
                best_lemma = self.__lm.best_ngram(start + 'or', start + 'our')
                if best_lemma is not None:
                    return best_lemma + end
        # standard-ys-e or standard-yz-e ?
        mids = ['ys', 'yz', 'is', 'iz']
        ends = ['ations', 'ation', 'ers', 'er', 'ing', 'ed', 'es', 'e']
        start_mid_end = _split_token(token, mids, ends)
        if start_mid_end is not None:
            start, mid, end = start_mid_end
            if len(start) > 2:
                best_lemma = self.__lm.best_ngram(start + mid[0] + 'ze', start + mid[0] + 'se')
                if best_lemma is not None:
                    return best_lemma[:-1] + end
        # defen-c-es or defen-s-es ?
        start_mid_end = _split_token(token, ['c', 's'], ['ives', 'ive', 'es', 'e'])
        if start_mid_end is not None:
            start, _, end = start_mid_end
            if len(start) > 2:
                best_lemma = self.__lm.best_ngram(start + 'se', start + 'ce')
                if best_lemma is not None:
                    return best_lemma[:-1] + end
        # catal-og-s or catal-ogue-s ?
        start_mid_end = _split_token(token, ['og', 'ogue'], ['s', ''])
        if start_mid_end is not None:
            start, _, end = start_mid_end
            if len(start) > 2:
                best_lemma = self.__lm.best_ngram(start + 'og', start + 'ogue')
                if best_lemma is not None:
                    return best_lemma + end
        # trav-el-ed or trav-el-led ?
        start_mid_end = _split_token(token, ['el', 'ell'], ['ing', 'ers', 'ed', 'er'])
        if start_mid_end is not None:
            start, _, end = start_mid_end
            if len(start) > 2:
                best_lemma = self.__lm.best_ngram(start + 'el' + end, start + 'ell' + end)
                if best_lemma is not None:
                    return best_lemma
        # leukaemia or leukemia ?
        if len(token) > 4 and token.find('ae') > -1:
            best_lemma = self.__lm.best_ngram(token.replace('ae', 'e'), token)
            if best_lemma is not None:
                return best_lemma
        # oestrogen or estrogen ?
        if len(token) > 4 and token.find('oe') > -1:
            best_lemma = self.__lm.best_ngram(token.replace('oe', 'e'), token)
            if best_lemma is not None:
                return best_lemma
        return token
