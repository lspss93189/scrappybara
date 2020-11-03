import numpy as np

import scrappybara.config as cfg
from scrappybara.utils.files import save_pkl_file, load_pkl_file


class Wordset(object):

    def __init__(self):
        self.__filepath = cfg.DATA_DIR / 'models' / 'word_vectors.pkl'
        self.__word_vector = None  # word => vector
        self.__zero_vector = np.zeros(cfg.WORD_VECTOR_SIZE)

    def __len__(self):
        return len(self.__word_vector) + 1

    def __getitem__(self, word):
        """Returns the vector of a given word"""
        try:
            return self.__word_vector[word]
        except KeyError:
            return self.__zero_vector

    def load(self):
        self.__word_vector = load_pkl_file(self.__filepath)
        return self

    def save(self, wordvec_folder, language_model):
        """Save dictionary of word=>vector as a pkl file"""
        file_path = wordvec_folder + '/glove.6B.%sd.txt' % str(cfg.WORD_VECTOR_SIZE)
        word_vector = {}
        with open(file_path, encoding=cfg.ENCODING) as txt_file:
            for line in txt_file:
                values = line.split()
                word = values[0]
                wordvec = values[1:]
                if language_model.has_ngram(word):
                    word_vector[word] = np.asarray(wordvec, dtype=np.float32)
        save_pkl_file(word_vector, self.__filepath)
