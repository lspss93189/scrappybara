import unittest

from scrappybara.langmodel.language_model import LanguageModel

_LM = LanguageModel()


class TestLanguageModel(unittest.TestCase):

    def test_top_ngrams(self):
        self.assertEqual(10, len(_LM.top_ngrams(1, 10)))
        self.assertEqual(10, len(_LM.top_ngrams(2, 10)))

    def test_next_word(self):
        self.assertEqual(2, len(_LM.next_word('might', limit=2)))

    def test_next_word_order_out_of_range(self):
        self.assertEqual(2, len(_LM.next_word('might have', limit=2)))

    def test_best_token(self):
        self.assertEqual('personnel', _LM.best_token('personnel', 'personal', before='talented'))
        self.assertEqual('personnel', _LM.best_token('personnel', 'personal', after='carriers'))

    def test_best_token_with_no_context(self):
        self.assertEqual('personal', _LM.best_token('personnel', 'personal'))

    def test_best_ngram(self):
        self.assertEqual('personal', _LM.best_ngram('personnel', 'personal'))

    def test_has_ngram(self):
        self.assertFalse(_LM.has_ngram('personal', min_count=0))
        self.assertFalse(_LM.has_ngram('personal', min_count=10000))
        self.assertTrue(_LM.has_ngram('personnel carriers'))

    def test_has_ngram_order_out_of_range(self):
        self.assertFalse(_LM.has_ngram('the very talented personnel carriers'))


if __name__ == '__main__':
    unittest.main()
