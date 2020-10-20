import unittest

from scrappybara.syntax.labelled_data import LabelledSentence, _arcs_are_crossing
from scrappybara.syntax.transitions import Trans


class TestLabelledData(unittest.TestCase):

    # LABELLED SENTENCE
    # -------------------------------------------------------------------------->

    def test_no_reduce(self):
        tuples = [('France', 'NOUN', 'SUBJ', 2), ('has', 'MAT', 'AUX', 2), ('changed', 'VERB', 'ROOT', -1),
                  ('its', 'DET', 'ART', 4), ('policy', 'NOUN', 'OBJ', 2), ('for', 'PREP', 'MARK', 7),
                  ('the', 'DET', 'ART', 7), ('disadvantaged', 'NOUN', 'CPL', 4)]
        self.assertListEqual(
            [(0, 1, Trans.SHIFT), (1, 2, Trans.LEFT), (0, 2, Trans.LEFT), (2, 3, Trans.SHIFT), (3, 4, Trans.LEFT),
             (2, 4, Trans.RIGHT), (4, 5, Trans.SHIFT), (5, 6, Trans.SHIFT), (6, 7, Trans.LEFT), (5, 7, Trans.LEFT),
             (4, 7, Trans.RIGHT)],
            LabelledSentence(0, tuples).transitions)

    def test_reduce_1(self):
        tuples = [('Japan', 'NOUN', 'SUBJ', 1), ('has', 'VERB', 'ROOT', -1), ('one', 'DET', 'ART', 4),
                  ('of', 'PREP', 'MARK', 2), ('the', 'DET', 'ART', 6), ('lowest', 'ADJ', 'CPL', 6),
                  ('rates', 'NOUN', 'OBJ', 1)]
        self.assertListEqual([
            (0, 1, Trans.LEFT), (1, 2, Trans.SHIFT), (2, 3, Trans.RIGHT), (3, 4, Trans.REDUCE), (2, 4, Trans.LEFT),
            (1, 4, Trans.SHIFT), (4, 5, Trans.SHIFT), (5, 6, Trans.LEFT), (4, 6, Trans.LEFT), (1, 6, Trans.RIGHT)],
            LabelledSentence(0, tuples).transitions)

    def test_reduce_2(self):
        tuples = [('A', 'DET', 'ART', 1), ('pie', 'NOUN', 'SUBJ', 2), ('has', 'VERB', 'ROOT', -1),
                  ('indeed', 'ADV', 'CPL', 2), ('apples', 'NOUN', 'OBJ', 2)]
        self.assertListEqual([
            (0, 1, Trans.LEFT), (1, 2, Trans.LEFT), (2, 3, Trans.RIGHT), (3, 4, Trans.REDUCE), (2, 4, Trans.RIGHT)],
            LabelledSentence(0, tuples).transitions)

    def test_chain_reduce(self):
        sample = [('Lost', 'PROPN', 'SUBJ', 3), ('in', 'PROPN', 'FLAT', 0), ('Translation', 'PROPN', 'FLAT', 1),
                  ('was', 'VERB', 'ROOT', -1), ('fun', 'ADJ', 'PROP', 3)]
        self.assertListEqual([
            (0, 1, Trans.RIGHT), (1, 2, Trans.RIGHT), (2, 3, Trans.REDUCE), (1, 3, Trans.REDUCE), (0, 3, Trans.LEFT),
            (3, 4, Trans.RIGHT)],
            LabelledSentence(0, sample).transitions)

    def test_sentence_1(self):
        sample = [('In', 'CONJ', 'MARK', 4), ('addition', 'CONJ', 'CPL', 0), ('there', 'THERE', 'SUBJ', 4),
                  ('will', 'MAT', 'AUX', 4), ('be', 'VERB', 'ROOT', -1), ('a', 'DET', 'ART', 10),
                  ('6ft', 'NUM', 'CPL', 7), ('deep', 'ADJ', 'CPL', 10), ('two', 'NUM', 'ART', 9),
                  ('story', 'NOUN', 'CPL', 10), ('porch', 'NOUN', 'EXIST', 4), ('across', 'PREP', 'MARK', 14),
                  ('the', 'DET', 'ART', 14), ('entire', 'ADJ', 'CPL', 14), ('back', 'NOUN', 'CPL', 10),
                  ('and', 'CONJ', 'NODEP', -1), ('30ft', 'NUM', 'CPL', 17), ('across', 'PREP', 'MARK', 19),
                  ('the', 'DET', 'ART', 19), ('front', 'NOUN', 'CPL', 10), ('.', 'PUNCT', 'NODEP', -1)]
        self.assertListEqual([
            (0, 1, Trans.RIGHT), (1, 2, Trans.SHIFT), (2, 3, Trans.SHIFT), (3, 4, Trans.LEFT), (2, 4, Trans.LEFT),
            (1, 4, Trans.REDUCE), (0, 4, Trans.LEFT), (4, 5, Trans.SHIFT), (5, 6, Trans.SHIFT), (6, 7, Trans.LEFT),
            (5, 7, Trans.SHIFT), (7, 8, Trans.SHIFT), (8, 9, Trans.LEFT), (7, 9, Trans.SHIFT), (9, 10, Trans.LEFT),
            (7, 10, Trans.LEFT), (5, 10, Trans.LEFT), (4, 10, Trans.RIGHT), (10, 11, Trans.SHIFT),
            (11, 12, Trans.SHIFT), (12, 13, Trans.SHIFT), (13, 14, Trans.LEFT), (12, 14, Trans.LEFT),
            (11, 14, Trans.LEFT), (10, 14, Trans.RIGHT), (14, 16, Trans.SHIFT), (16, 17, Trans.LEFT),
            (14, 17, Trans.SHIFT), (17, 18, Trans.SHIFT), (18, 19, Trans.LEFT), (17, 19, Trans.LEFT),
            (14, 19, Trans.REDUCE), (10, 19, Trans.RIGHT)],
            LabelledSentence(0, sample).transitions)

    # CROSSING ARCS
    # -------------------------------------------------------------------------->

    def test_arcs_are_crossing_true(self):
        self.assertEqual(True, _arcs_are_crossing((float('-inf'), 3), (2, 4)))
        self.assertEqual(True, _arcs_are_crossing((1, 3), (2, 4)))
        self.assertEqual(True, _arcs_are_crossing((4, 2), (3, 1)))

    def test_arcs_are_crossing_false(self):
        self.assertEqual(False, _arcs_are_crossing((1, 10), (2, 3)))
        self.assertEqual(False, _arcs_are_crossing((2, 1), (4, 3)))
        self.assertEqual(False, _arcs_are_crossing((1, 10), (2, 10)))


if __name__ == '__main__':
    unittest.main()
