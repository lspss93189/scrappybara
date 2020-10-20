import collections

import numpy as np

from scrappybara.langmodel.smoother import Smoother, DataSlice
from scrappybara.langmodel.smoother import calc_ngrams_multithread
from scrappybara.utils.mutables import append_to_dict_list


class ModifiedKneserNeyNotEnoughDataError(Exception):

    def __init__(self):
        super().__init__("Input data is not rich enough for 'modified_kneser_ney' smoothing.")


def _prepare_mkn(ngrams, last_order):
    """Calculate all counts necessary prior to smoothing"""
    lm_ngrams = {}  # order => list of ngrams
    wcs = collections.Counter()
    wc1 = collections.Counter()
    wc2 = collections.Counter()
    wc3 = collections.Counter()
    n1 = collections.Counter()  # Number of ngrams with count 1
    n2 = collections.Counter()  # Number of ngrams with count 2
    n3 = collections.Counter()  # Number of ngrams with count 3
    n4 = collections.Counter()  # Number of ngrams with count 4
    for ngram in ngrams:
        # n counts
        if ngram.count == 1:
            n1[ngram.order] += 1
        elif ngram.count == 2:
            n2[ngram.order] += 1
        elif ngram.count == 3:
            n3[ngram.order] += 1
        elif ngram.count == 4:
            n4[ngram.order] += 1
        # Wildcards
        if ngram.order > 1:
            wcs['%s %s' % ('•', ' '.join(ngram.tokens[1:]))] += 1  # • ngram
            wc = '%s %s' % (' '.join(ngram.tokens[:-1]), '•')  # ngram •
            if ngram.count == 1:
                wc1[wc] += 1
            elif ngram.count == 2:
                wc2[wc] += 1
            else:
                wc3[wc] += 1
        if ngram.order > 2:
            wcs['%s %s %s' % ('•', ' '.join(ngram.tokens[1:-1]), '•')] += 1  # • ngram •
        append_to_dict_list(lm_ngrams, ngram.order, ngram)
    # Calculage discounting values
    d1 = {}
    d2 = {}
    d3 = {}
    for order in range(2, last_order + 1):
        if any([n1[order] == 0, n2[order] == 0, n3[order] == 0, n4[order] == 0]):
            raise ModifiedKneserNeyNotEnoughDataError()
        else:
            y = n1[order] / (n1[order] + 2. * n2[order])
            d1[order] = 1. - (2. * y * n2[order] / n1[order])
            d2[order] = 2. - (3. * y * n3[order] / n2[order])
            d3[order] = 3. - (4. * y * n4[order] / n3[order])
    return lm_ngrams, wcs, wc1, wc2, wc3, d1, d2, d3


class _DataSlice(DataSlice):

    def __init__(self, operands):
        super().__init__()
        self.__operands = operands

    def calc_unigrams(self):
        self.np_probas = self.__operands[0] / self.__operands[1]

    def calc_multigrams(self):
        self.np_probas = _calc_proba_recursive(self.__operands)


def _calc_proba_recursive(operands):
    """Calculate probability by unfolding mkn_arrays recursively"""
    if len(operands) == 1:
        return operands[0]
    np_zero = np.zeros(len(operands[0]))
    np_l_counts = operands[0]
    np_discounts = operands[1]
    np_lr_counts = operands[2]
    np_r1_counts = operands[3]
    np_r2_counts = operands[5]
    np_r3_counts = operands[7]
    # Calculate probability
    np_cc = np.maximum(np_l_counts - np_discounts, np_zero) / np_lr_counts
    np_r1_counts = np_r1_counts * operands[4]
    np_r2_counts = np_r2_counts * operands[6]
    np_r3_counts = np_r3_counts * operands[8]
    np_weight = (np_r1_counts + np_r2_counts + np_r3_counts) / np_lr_counts
    return np_cc + np_weight * _calc_proba_recursive(operands[-1])


def _calc_unigrams(data_slice):
    data_slice.calc_unigrams()
    return data_slice


def _calc_multigrams(data_slice):
    data_slice.calc_multigrams()
    return data_slice


class MKNSmoother(Smoother):

    def __init__(self, ngrams, last_order, nb_processes):
        lm_ngrams, wcngrams, wc1, wc2, wc3, d1, d2, d3 = _prepare_mkn(ngrams, last_order)
        super().__init__(lm_ngrams, last_order, nb_processes)
        # Constants
        self.__d1 = d1
        self.__d2 = d2
        self.__d3 = d3
        self.nb_uni = len(lm_ngrams.get(1, []))
        # Lookups
        self.__wcs_lookup = wcngrams
        self.__wcs1_lookup = wc1
        self.__wcs2_lookup = wc2
        self.__wcs3_lookup = wc3
        self.__ngrams_lookup = {}
        for lm_ngram in [ngram for i in lm_ngrams for ngram in lm_ngrams[i]]:
            self.__ngrams_lookup[lm_ngram.text] = lm_ngram
        self.__uni_mkns_lookup = {}

    def __call__(self):
        # Unigrams
        np_probas = self.calc_unigram_probas()
        for idx, proba in enumerate(np_probas):
            self._ngrams[1][idx].proba = proba
        # Higher orders
        for order in range(2, self._last_order + 1):
            np_probas = self.calc_higher_order_probas(order)
            for idx, proba in enumerate(np_probas):
                self._ngrams[order][idx].proba = proba
        return self

    def __discount(self, order, countc):
        if countc == 0:
            return 0.0
        if countc == 1:
            return self.__d1[order]
        if countc == 2:
            return self.__d2[order]
        return self.__d3[order]

    def __mkn_pack(self, ngram, order):
        """Calculates all counts for an ngram"""
        assert order > 1
        # Absolute or continuous counts
        start_order = ngram.order
        if start_order == order:  # Highest order of ngram
            cl = ngram.count
            cl_d = self.__discount(order, cl)
            crl = self.__ngrams_lookup[ngram.without_last_token].count
            last_wc = ngram.wc_last_token
            last_wc_order = order
        else:
            lower = self.__ngrams_lookup[ngram.lower_order(order)]
            cl = self.__wcs_lookup[lower.prepend_wc]
            cl_d = self.__discount(order + 1, cl)
            crl = self.__wcs_lookup[lower.continuous_ngram]
            last_wc = lower.wc_last_token
            last_wc_order = order
        n1 = self.__wcs1_lookup[last_wc]
        n1_d = self.__d1[last_wc_order]
        n2 = self.__wcs2_lookup[last_wc]
        n2_d = self.__d2[last_wc_order]
        n3 = self.__wcs3_lookup[last_wc]
        n3_d = self.__d3[last_wc_order]
        return cl, cl_d, crl, n1, n1_d, n2, n2_d, n3, n3_d

    def __mkn_arrays(self, start_order, order, process_range):
        """Recursively prepares numpy arrays for probability calculation"""
        assert start_order > 1
        batch_size = len(process_range)
        if order == 1:  # Lowest order
            uni_mkns = np.empty(batch_size)
            for i in process_range:
                uni_mkns[i - process_range[0]] = self.__uni_mkns_lookup[self._ngrams[start_order][i].last_token]
            return [uni_mkns]
        # Higher order
        # Continious coeff
        np_l_counts = np.empty(batch_size)
        np_l_discounts = np.empty(batch_size)
        np_lr_counts = np.empty(batch_size)
        # Lower order weighting
        np_r1_counts = np.empty(batch_size)
        np_r2_counts = np.empty(batch_size)
        np_r3_counts = np.empty(batch_size)
        r1_d = r2_d = r3_d = None
        # Fill up arrays
        for i in process_range:
            ngram = self._ngrams[start_order][i]
            j = i - process_range[0]
            ops = self.__mkn_pack(ngram, order)
            np_l_counts[j] = ops[0]
            np_l_discounts[j] = ops[1]
            np_lr_counts[j] = ops[2]
            np_r1_counts[j] = ops[3]
            r1_d = ops[4]
            np_r2_counts[j] = ops[5]
            r2_d = ops[6]
            np_r3_counts[j] = ops[7]
            r3_d = ops[8]
        return [np_l_counts, np_l_discounts, np_lr_counts, np_r1_counts, r1_d, np_r2_counts,
                r2_d, np_r3_counts, r3_d, self.__mkn_arrays(start_order, order - 1, process_range)]

    def discount_1(self, order):
        return self.__d1[order]

    def discount_2(self, order):
        return self.__d2[order]

    def discount_3(self, order):
        return self.__d3[order]

    def calc_unigram_probas(self):
        nb_bigrams = len(self._ngrams.get(2, []))
        data_slices = []
        for process_range in self._process_ranges(self.nb_uni):
            np_uni_mkn = np.empty(len(process_range))
            for i in process_range:
                unigram = self._ngrams[1][i]
                np_uni_mkn[i - process_range[0]] = self.__wcs_lookup[unigram.prepend_wc]
            data_slices.append(_DataSlice([np_uni_mkn, nb_bigrams]))
        np_mkn = calc_ngrams_multithread(data_slices, _calc_unigrams, self._nb_processes)
        for i in range(self.nb_uni):
            self.__uni_mkns_lookup[self._ngrams[1][i].text] = np_mkn[i]
        return np_mkn

    def calc_higher_order_probas(self, order):
        assert order > 1
        data_slices = []
        for process_range in self._process_ranges(len(self._ngrams.get(order, []))):
            data_slices.append(_DataSlice(self.__mkn_arrays(order, order, process_range)))
        return calc_ngrams_multithread(data_slices, _calc_multigrams, self._nb_processes)
