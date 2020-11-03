import numpy as np

import scrappybara.config as cfg
from scrappybara.syntax.dependencies import Dep
from scrappybara.syntax.tags import Tag


def _pad_array(array, dim):
    """Pads array with 0's"""
    result = np.zeros(dim, dtype=np.int32)
    array = np.array(array[-dim:], dtype=np.int32)
    result[:len(array)] = array
    return result


def _fill_columns(matrix, dim):
    """Fill matrix columns with 0's"""
    arrays_len = len(matrix)
    result = (np.zeros((arrays_len, dim), dtype=np.int32))
    for idx, array in enumerate(matrix):
        result[idx] = _pad_array(array, dim)
    return result


def _pad_char_codes(matrix):
    """Pads sentence's char codes"""
    empty_arrays = _fill_columns([[] for _ in range(cfg.PADDED_SENT_LENGTH - len(matrix))],
                                 cfg.PADDED_WORD_LENGTH)
    padded_arrays = _fill_columns(matrix[:cfg.PADDED_SENT_LENGTH], cfg.PADDED_WORD_LENGTH)
    return np.concatenate((padded_arrays, empty_arrays))


def _pad_word_vectors(matrix):
    """Pads sentence's word vectors"""
    assert all([len(array) == len(matrix[0]) for array in matrix])
    result = (np.zeros((cfg.PADDED_SENT_LENGTH, len(matrix[0])), dtype=np.float32))
    for idx, array in enumerate(matrix):
        result[idx] = array
    return result


def _encode_chars(token, charset):
    if len(token) > cfg.MAX_WORD_LENGTH:
        token = token[len(token) - cfg.MAX_WORD_LENGTH:]  # Truncate beginning of word if too long
    token = '†' + token + '‡'
    return [charset[char] for char in token]


class SentenceTooLongError(Exception):

    def __init__(self):
        super().__init__("Sentence is too long.")


def make_masks(idx_1, idx_2):
    """Idxs are padding-shifted"""

    def _make_mask(_idx):
        _mask = [False] * cfg.PADDED_SENT_LENGTH
        _mask[_idx] = True
        return _mask

    return _make_mask(idx_1), _make_mask(idx_2)


def vectorize_sentence(tokens, standards, charset, wordset):
    """Returns sequence length & padded numpy arrays"""
    if len(tokens) > cfg.MAX_SENT_LENGTH:
        raise SentenceTooLongError()
    char_codes = _pad_char_codes([_encode_chars(token, charset) for token in ['ʃʃʃ'] + tokens + ['ʄʄʄ']])
    word_vectors = _pad_word_vectors([wordset[standard] for standard in ['ʃʃʃ'] + standards + ['ʄʄʄ']])
    return len(tokens), char_codes, word_vectors


class _TrainingSample(object):

    def __init__(self, tokens, standards, charset, wordset):
        _, self._char_ids, self._word_vectors = vectorize_sentence(tokens, standards, charset, wordset)

    @staticmethod
    def _tag_ids(tags):
        return _pad_array([Tag.PAD.value] + [tag.value for tag in tags] + [Tag.PAD.value], cfg.PADDED_SENT_LENGTH)

    @staticmethod
    def _dep_ids(deps):
        return _pad_array([Dep.PAD.value] + [dep.value for dep in deps] + [Dep.PAD.value], cfg.PADDED_SENT_LENGTH)


class PTagsSample(_TrainingSample):

    def __init__(self, tokens, standards, tags, charset, wordset):
        super().__init__(tokens, standards, charset, wordset)
        self.__tag_ids = self._tag_ids(tags)

    @property
    def training_mats(self):
        return self._char_ids, self._word_vectors, self.__tag_ids


class PDepsSample(_TrainingSample):

    def __init__(self, tokens, standards, tags, deps, charset, wordset):
        super().__init__(tokens, standards, charset, wordset)
        self.__tag_ids = self._tag_ids(tags)
        self.__dep_ids = self._dep_ids(deps)

    @property
    def training_mats(self):
        return self.__tag_ids, self._char_ids, self._word_vectors, self.__dep_ids


class TransSample(_TrainingSample):

    def __init__(self, tokens, standards, tags, deps, idx_1, idx_2, transition, charset, wordset):
        super().__init__(tokens, standards, charset, wordset)
        self.__tag_ids = self._tag_ids(tags)
        self.__dep_ids = self._dep_ids(deps)
        self.__mask_1, self.__mask_2 = make_masks(idx_1 + 1, idx_2 + 1)
        self.__trans_code = transition.value

    @property
    def training_mats(self):
        return self.__tag_ids, self.__dep_ids, self._char_ids, self._word_vectors, self.__mask_1, self.__mask_2, \
               self.__trans_code
