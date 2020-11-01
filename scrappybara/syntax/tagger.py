import scrappybara.config as cfg
from scrappybara.syntax.tags import Tag
from scrappybara.syntax.training_samples import vectorize_sentence
from scrappybara.utils.multithreading import run_multithreads
from scrappybara.utils.mutables import make_batches


class Tagger(object):

    def __init__(self, charset, wordset, ptags_model, batch_size):
        self.__charset = charset
        self.__wordset = wordset
        self.__ptags_model = ptags_model
        self.__batch_size = batch_size

    def __call__(self, token_lists):
        """Tags sentences by batch"""
        mats = run_multithreads(token_lists, self.__vectorize_sentence, cfg.NB_PROCESSES)
        batches = make_batches(mats, self.__batch_size)
        tag_lists = []
        for batch in batches:
            seq_lengths, char_codes, word_vectors = zip(*batch)
            tag_codes = self.__predict_tags(char_codes, word_vectors)
            for idx, seq_length in enumerate(seq_lengths):
                tag_lists.append([Tag(code) for code in tag_codes[idx][1:seq_length - 1]])
        return tag_lists

    def __vectorize_sentence(self, tokens):
        return vectorize_sentence(tokens, self.__charset, self.__wordset)

    def __predict_tags(self, char_codes, word_vectors):
        return self.__ptags_model.predict(char_codes, word_vectors)
