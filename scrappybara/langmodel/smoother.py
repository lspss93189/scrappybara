import abc

import numpy as np

from scrappybara.utils.multithreading import run_multithreads


class DataSlice(abc.ABC):
    """Probability calculator for a single data slice.
    Used for multithreading the calculation of probabilities.
    """

    def __init__(self):
        self.np_probas = None


def calc_ngrams_multithread(data_slices, process, nb_processes):
    data_slices = run_multithreads(data_slices, process, nb_processes)
    np_probas = data_slices[0].np_probas
    for data_slice in data_slices[1:]:
        np_probas = np.concatenate((np_probas, data_slice.np_probas))
    return np_probas


class Smoother(abc.ABC):

    def __init__(self, ngrams, last_order, nb_processes):
        self._ngrams = ngrams  # order => list of ngrams
        self._nb_processes = nb_processes
        self._last_order = last_order

    @abc.abstractmethod
    def __call__(self):
        """Calculate probabilities for all orders"""
        return self  # Child class' method must return self

    def _process_ranges(self, nb_samples):
        """Returns data ranges for each multithreaded process"""
        marks = np.linspace(0, nb_samples, self._nb_processes + 1, dtype=int)
        return [range(marks[i], marks[i + 1]) for i in range(self._nb_processes)]

    def ngrams(self, order):
        return self._ngrams.get(order, [])
