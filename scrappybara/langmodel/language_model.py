import math

import scrappybara.config as cfg
from scrappybara.langmodel.token_context import TokenContext
from scrappybara.preprocessing.tokenizer import Tokenizer
from scrappybara.utils.files import load_pkl_file
from scrappybara.utils.mutables import append_to_dict_list


class LanguageModel(object):
    __min_counts = (1, 1)  # Load all unigrams & bigrams

    def __init__(self):
        """Pass the min count for each order needed.
        Examples:
          * If only unigrams are needed with min count 1, instantiate LanguageModel(1)
          * To get unigrams with mincount 10 and bigrams with mincount 5, instantiate LanguageModel(10, 5)
        """
        self.__max_order = len(self.__min_counts)
        self.__ngrams_details = {}  # ngram => tuple (count, proba, logp)
        self.__unk = (0, 0.0, float('-inf'))  # Unknown ngram (count=0, proba=0.0, logp=-inf)
        self.__tokenize = Tokenizer()
        # Load ngrams
        for idx, min_count in enumerate(self.__min_counts):
            order = idx + 1
            for text, count, proba in load_pkl_file(cfg.DATA_DIR / 'langmodel' / ('%d_grams.pkl' % order)):
                if count >= min_count:
                    self.__ngrams_details[text] = (count, proba, math.log(proba))
        # Build next_token dict
        self.__next_tokens = {}  # ngram => list of tuples (token, proba) ordered by descending proba
        if self.__max_order > 1:
            for ngram, details in self.__ngrams_details.items():
                tokens = ngram.split()
                if len(tokens) > 1:
                    append_to_dict_list(self.__next_tokens, ' '.join(tokens[:-1]), (tokens[-1], details[1]))
        for ngram, next_tokens in self.__next_tokens.items():
            next_tokens.sort(key=lambda x: x[1], reverse=True)

    def __len__(self):
        return len(self.__ngrams_details)

    def __contains__(self, ngram):
        return ngram in self.__ngrams_details

    def __logp(self, ngram):
        """Log-probability"""
        return self.__ngrams_details.get(ngram, self.__unk)[2]

    def __logps(self, token_context):
        """Returns list of log-probabilities sorted in descending order.
        e.g. for the ngram 'a hat', it will return [logp('a hat'), logp('hat')]
        """
        probas = []
        for i in range(self.__max_order, 1, -1):
            candidates = token_context.candidates(i)
            if candidates:
                probas.append(max([self.__logp(ngram) for ngram in candidates]))
            else:
                probas.append(float('-inf'))
        probas.append(self.__logp(token_context.token))
        return probas

    def top_ngrams(self, order, limit=None):
        ngrams = []
        for ngram, details in self.__ngrams_details.items():
            if len(ngram.split()) == order:
                ngrams.append((ngram, *details[:-1]))
        sorted_ngrams = sorted(ngrams, key=lambda x: x[2], reverse=True)
        return sorted_ngrams[:limit]

    def next_word(self, text, limit=None):
        tokens = self.__tokenize(text)
        for i in range(self.__max_order - 1, 0, -1):
            try:
                return self.__next_tokens[' '.join(tokens[-i:])][:limit]
            except KeyError:
                continue
        return []

    def best_token(self, *tokens, before=None, after=None):
        """Finds the best token among a list of candidates.
        E.g. if we want to know the best token between 'personnel' & 'personal', given the context:
          "hire best [personnel/personal] today"
          Call: best_token('personnel', 'personal', before='hire best', after='today')
        If none of the tokens have been found, returns None.
        """
        if not any([token in self.__ngrams_details for token in tokens]):
            return None
        tokens_before = self.__tokenize(before) or []
        tokens_after = self.__tokenize(after) or []
        token_contexts = [TokenContext(token, tokens_before, tokens_after) for token in tokens]
        tprobas = {tuple(self.__logps(token_context)): idx for idx, token_context in enumerate(token_contexts)}
        return tokens[tprobas[max(tprobas.keys())]]

    def best_ngram(self, *ngrams):
        """Returns the ngram with the highest probability among the selection.
        If none of the ngrams has been found, returns None.
        """
        if not any([ngram in self.__ngrams_details for ngram in ngrams]):
            return None
        token_logp_tuples = [(ngram, self.__logp(ngram)) for ngram in ngrams]
        token_logp_tuples.sort(key=lambda x: x[1], reverse=True)
        return token_logp_tuples[0][0]

    def has_ngram(self, ngram, min_count=1):
        if min_count < 1:
            return False
        return self.__ngrams_details.get(ngram, self.__unk)[0] >= min_count
