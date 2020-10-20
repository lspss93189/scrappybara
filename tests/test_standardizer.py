import unittest

from scrappybara.langmodel.language_model import LanguageModel
from scrappybara.normalization.standardizer import Standardizer

_STANDARDIZE = Standardizer(LanguageModel())


class TestStandardizer(unittest.TestCase):

    def test_ending_our(self):
        self.assertEqual('color', _STANDARDIZE('colour'))
        self.assertEqual('coloring', _STANDARDIZE('colouring'))
        self.assertEqual('colored', _STANDARDIZE('coloured'))
        self.assertEqual('colors', _STANDARDIZE('colours'))

    def test_ending_ise(self):
        self.assertEqual('realize', _STANDARDIZE('realise'))
        self.assertEqual('realizations', _STANDARDIZE('realisations'))
        self.assertEqual('realization', _STANDARDIZE('realisation'))
        self.assertEqual('realizers', _STANDARDIZE('realisers'))
        self.assertEqual('realizer', _STANDARDIZE('realiser'))
        self.assertEqual('realizing', _STANDARDIZE('realising'))
        self.assertEqual('realized', _STANDARDIZE('realised'))
        self.assertEqual('realizes', _STANDARDIZE('realises'))

    def test_ending_yse(self):
        self.assertEqual('analyzes', _STANDARDIZE('analyses'))

    def test_ending_ce(self):
        self.assertEqual('defense', _STANDARDIZE('defence'))
        self.assertEqual('defensives', _STANDARDIZE('defencives'))
        self.assertEqual('defensive', _STANDARDIZE('defencive'))
        self.assertEqual('defenses', _STANDARDIZE('defences'))

    def test_ending_og(self):
        self.assertEqual('dialogue', _STANDARDIZE('dialog'))
        self.assertEqual('dialogues', _STANDARDIZE('dialogs'))

    def test_double_consonants(self):
        self.assertEqual('travelling', _STANDARDIZE('traveling'))
        self.assertEqual('travelled', _STANDARDIZE('traveled'))
        self.assertEqual('travellers', _STANDARDIZE('travelers'))
        self.assertEqual('traveller', _STANDARDIZE('traveler'))

    def test_ae(self):
        self.assertEqual('leukemia', _STANDARDIZE('leukaemia'))

    def test_oe(self):
        self.assertEqual('oenophile', _STANDARDIZE('oenophile'))

    def test_padding(self):
        self.assertEqual('ʃʃʃ', _STANDARDIZE('ʃʃʃ'))
        self.assertEqual('ʄʄʄ', _STANDARDIZE('ʄʄʄ'))


if __name__ == '__main__':
    unittest.main()
