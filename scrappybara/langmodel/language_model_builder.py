import multiprocessing

import scrappybara.config as cfg
from scrappybara.exceptions import ArgumentValueError
from scrappybara.langmodel.mkn_smoother import MKNSmoother
from scrappybara.langmodel.mle_smoother import MLESmoother
from scrappybara.langmodel.ngram_store import NgramStore
from scrappybara.langmodel.ngrams_extraction import extract_ngrams
from scrappybara.preprocessing.sentencizer import Sentencizer
from scrappybara.utils.files import save_pkl_file
from scrappybara.utils.logger import Logger
from scrappybara.utils.timer import Timer


class ModifiedKneserNeyMinOrderError(Exception):

    def __init__(self):
        super().__init__("'modified_kneser_ney' requires 'max_order' to be at least 2.")


class LanguageModelBuilder(object):
    __smoothing_methods = {'modified_kneser_ney', 'maximum_likelihood_estimation'}

    def __init__(self, max_order, smoothing, output_path):
        Logger.info('BUILD LANGUAGE MODEL: max_order=%d, smoothing=%s' % (max_order, smoothing))
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
        self.__output_path = output_path  # pathlib.Path

    def __call__(self, text_iterator):
        """Extracts ngrams & calculates probabilities"""
        timer = Timer()
        # Extract ngrams
        store = NgramStore()
        consumed = False
        nb_texts = 0
        while not consumed:
            batch = []
            for i in range(cfg.NB_PROCESSES):
                try:
                    batch.append(next(text_iterator))
                    nb_texts += 1
                except StopIteration:
                    consumed = True
                    break
            with multiprocessing.Pool(cfg.NB_PROCESSES) as pool:
                texts_tokens = pool.map(self.__sentencize, batch)
            for text_tokens in texts_tokens:
                for n in range(1, self.__max_order + 1):
                    for ngram in extract_ngrams(text_tokens, n):
                        store.make_ngram(ngram)
            Logger.info('{:,} texts processed in {}'.format(nb_texts, timer.lap_time))
        # Calculate probas
        smoother = self.__smoother(store.ngrams, self.__max_order, cfg.NB_PROCESSES)()
        # Write ngrams
        for n in range(1, self.__max_order + 1):
            self.__write_ngram_file(n, smoother.ngrams(n), timer)
        Logger.info('Probabilities calculated in {}'.format(timer.lap_time))

    def __write_ngram_file(self, order, ngrams, timer):
        ngram_tuples = [(ngram.text, ngram.count, ngram.proba) for ngram in ngrams if ngram.proba > 0.0]
        save_pkl_file(ngram_tuples, self.__output_path / ('%d_grams.pkl' % order))
        Logger.info('Wrote {:,} {}-grams'.format(len(ngrams), order))
        Logger.info('Total time: {}'.format(timer.total_time))
