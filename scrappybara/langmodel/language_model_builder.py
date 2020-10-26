import multiprocessing

from scrappybara.exceptions import ArgumentValueError
from scrappybara.langmodel.mkn_smoother import MKNSmoother
from scrappybara.langmodel.mle_smoother import MLESmoother
from scrappybara.langmodel.ngram_store import NgramStore
from scrappybara.langmodel.ngrams_extraction import extract_ngrams
from scrappybara.preprocessing.sentencizer import Sentencizer
from scrappybara.utils.files import save_pkl_file
from scrappybara.utils.timer import Timer


class ModifiedKneserNeyMinOrderError(Exception):

    def __init__(self):
        super().__init__("'modified_kneser_ney' requires 'max_order' to be at least 2.")


class LanguageModelBuilder(object):
    __smoothing_methods = {'modified_kneser_ney', 'maximum_likelihood_estimation'}

    def __init__(self, max_order, smoothing='modified_kneser_ney', nb_processes=multiprocessing.cpu_count()):
        if smoothing not in self.__smoothing_methods:
            raise ArgumentValueError('smoothing', smoothing, self.__smoothing_methods)
        if smoothing == 'modified_kneser_ney' and max_order < 2:
            raise ModifiedKneserNeyMinOrderError()
        self.__max_order = max_order
        self.__sentencize = Sentencizer()
        if smoothing == 'modified_kneser_ney':
            self.__smoother = MKNSmoother
        else:
            self.__smoother = MLESmoother
        self.__nb_processes = nb_processes

    def __call__(self, text_iterator):
        """Extracts ngrams & calculates probabilities"""
        timer = Timer()
        # Extract ngrams
        store = NgramStore()
        consumed = False
        nb_texts = 0
        while not consumed:
            batch = []
            for i in range(self.__nb_processes):
                try:
                    batch.append(next(text_iterator))
                    nb_texts += 1
                except StopIteration:
                    consumed = True
                    break
            with multiprocessing.Pool(self.__nb_processes) as pool:
                texts_tokens = pool.map(self.__sentencize, batch)
            for text_tokens in texts_tokens:
                for n in range(1, self.__max_order + 1):
                    for ngram in extract_ngrams(text_tokens, n):
                        store.make_ngram(ngram)
            print('\rExtracting ngrams - texts processed: %d' % nb_texts, end='')
        # Calculate probas
        print('\nCalculating probabilities...', end='')
        smoother = self.__smoother(store.ngrams, self.__max_order, self.__nb_processes)()
        print(' [DONE]')
        # Write ngrams of higher orders
        for n in range(1, self.__max_order + 1):
            self.__write_ngram_file(n, smoother.ngrams(n))
        print('Total execution time: {}'.format(timer.total_time))

    @staticmethod
    def __write_ngram_file(order, ngrams):
        ngram_tuples = [(ngram.text, ngram.count, ngram.proba) for ngram in ngrams if ngram.proba > 0.0]
        save_pkl_file(ngram_tuples, 'data/langmodel', '%d_grams.pkl' % order)
        print('Wrote {:,} {}-grams'.format(len(ngrams), order))
