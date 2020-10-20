import numpy as np

from scrappybara.langmodel.smoother import Smoother, DataSlice
from scrappybara.langmodel.smoother import calc_ngrams_multithread
from scrappybara.utils.mutables import append_to_dict_list


class _DataSlice(DataSlice):

    def __init__(self, np_counts, total_count):
        super().__init__()
        self.__np_counts = np_counts
        self.__total_count = total_count

    def calc(self):
        self.np_probas = self.__np_counts / self.__total_count


def _calc_ngrams(data_slice):
    data_slice.calc()
    return data_slice


class MLESmoother(Smoother):

    def __init__(self, ngrams, last_order, nb_processes):
        ngrams_dict = {}  # order => list of ngrams
        self.__total_counts = {order: 0 for order in range(1, last_order + 1)}  # order => total_count
        for ngram in ngrams:
            self.__total_counts[ngram.order] += ngram.count
            append_to_dict_list(ngrams_dict, ngram.order, ngram)
        super().__init__(ngrams_dict, last_order, nb_processes)

    def __call__(self):
        for order in range(1, self._last_order + 1):
            data_slices = []
            ngrams = self._ngrams[order]
            for process_range in self._process_ranges(len(self._ngrams.get(order, []))):
                np_counts = np.array([ngrams[i].count for i in process_range])
                data_slices.append(_DataSlice(np_counts, self.__total_counts[order]))
            np_probas = calc_ngrams_multithread(data_slices, _calc_ngrams, self._nb_processes)
            for idx, proba in enumerate(np_probas):
                self._ngrams[order][idx].proba = proba
        return self
