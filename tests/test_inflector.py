import unittest

from scrappybara.langmodel.language_model import LanguageModel
from scrappybara.normalization.inflector import Inflector
from scrappybara.utils.files import load_dict_from_txt_file
from scrappybara.utils.mutables import reverse_dict

_PP = load_dict_from_txt_file('data/english', 'irregular_past_participles.txt')
_REVERSED_PP = reverse_dict(_PP)

_INFLECT = Inflector(LanguageModel(), _REVERSED_PP)


class TestInflector(unittest.TestCase):

    def test_past_participle(self):
        self.assertEqual('made', _INFLECT.past_participle('make'))
        self.assertEqual('tied', _INFLECT.past_participle('tie'))
        self.assertEqual('applied', _INFLECT.past_participle('apply'))
        self.assertEqual('pruned', _INFLECT.past_participle('prune'))
        self.assertEqual('travelled', _INFLECT.past_participle('travel'))
        self.assertEqual('played', _INFLECT.past_participle('play'))


if __name__ == '__main__':
    unittest.main()
