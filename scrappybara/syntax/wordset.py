import numpy as np

import scrappybara.config as cfg
from scrappybara.normalization.standardizer import Standardizer
from scrappybara.utils.files import save_pkl_file, load_pkl_file


class Wordset(object):

    def __init__(self, language_model):
        self.__lm = language_model
        self.__standardize = Standardizer(language_model)
        self.__filepath = ('data/models', 'word_vectors.pkl')
        self.__word_vector = None  # word => vector
        self.__zero_vector = np.zeros(cfg.WORD_VECTOR_SIZE)

    def __len__(self):
        return len(self.__word_vector) + 1

    def __getitem__(self, word):
        """Returns the vector of a given word"""
        try:
            word = self.__standardize(word)
            return self.__word_vector[word]
        except KeyError:
            return self.__zero_vector

    def load(self):
        self.__word_vector = load_pkl_file(*self.__filepath)
        return self

    def save(self, wordvec_folder):
        """Save dictionary of word=>vector as a pkl file"""
        file_path = wordvec_folder + '/glove.6B.%sd.txt' % str(cfg.WORD_VECTOR_SIZE)
        word_vector = {}
        with open(file_path, encoding=cfg.ENCODING) as txt_file:
            for line in txt_file:
                values = line.split()
                word = values[0]
                wordvec = values[1:]
                if self.__lm.has_ngram(word):
                    word_vector[word] = np.asarray(wordvec, dtype=np.float32)
        save_pkl_file(word_vector, *self.__filepath)
