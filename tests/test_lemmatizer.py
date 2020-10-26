import unittest

from scrappybara.langmodel.language_model import LanguageModel
from scrappybara.normalization.lemmatizer import Lemmatizer
from scrappybara.normalization.suffixes import Suffix
from scrappybara.syntax.tags import Tag
from scrappybara.utils.files import load_dict_from_txt_file, load_set_from_txt_file
from scrappybara.utils.mutables import reverse_dict

_ADJS = load_set_from_txt_file('data/english', 'adjectives.txt')
_PRET = load_dict_from_txt_file('data/english', 'irregular_preterits.txt')
_PP = load_dict_from_txt_file('data/english', 'irregular_past_participles.txt')
_PLUR = load_dict_from_txt_file('data/english', 'irregular_plurals.txt')
_COMP = load_dict_from_txt_file('data/english', 'irregular_comparatives.txt')
_SUP = load_dict_from_txt_file('data/english', 'irregular_superlatives.txt')
_REVERSED_PP = reverse_dict(_PP)

_LEMMATIZE = Lemmatizer(LanguageModel(), _ADJS, _PRET, _PP, _PLUR, _COMP, _SUP, _REVERSED_PP)


class TestLemmatization(unittest.TestCase):

    # VERBS
    # -------------------------------------------------------------------------->

    def test_verb_be(self):
        lemma, suffix = _LEMMATIZE("'m", Tag.VERB)
        self.assertEqual('be', lemma)
        self.assertEqual(None, suffix)

        lemma, suffix = _LEMMATIZE('am', Tag.VERB)
        self.assertEqual('be', lemma)
        self.assertEqual(None, suffix)

        lemma, suffix = _LEMMATIZE("'re", Tag.VERB)
        self.assertEqual('be', lemma)
        self.assertEqual(None, suffix)

        lemma, suffix = _LEMMATIZE('are', Tag.VERB)
        self.assertEqual('be', lemma)
        self.assertEqual(None, suffix)

        lemma, suffix = _LEMMATIZE("'s", Tag.VERB)
        self.assertEqual('be', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

        lemma, suffix = _LEMMATIZE('is', Tag.VERB)
        self.assertEqual('be', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_format(self):
        lemma, suffix = _LEMMATIZE('formatting', Tag.VERB)
        self.assertEqual('format', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('formatted', Tag.VERB)
        self.assertEqual('format', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('re-formatted', Tag.VERB)
        self.assertEqual('re-format', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('reformatted', Tag.VERB)
        self.assertEqual('reformat', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('formats', Tag.VERB)
        self.assertEqual('format', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_picnic(self):
        lemma, suffix = _LEMMATIZE('picnicking', Tag.VERB)
        self.assertEqual('picnic', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('picnicked', Tag.VERB)
        self.assertEqual('picnic', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('picnicks', Tag.VERB)
        self.assertEqual('picnic', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_roll(self):
        lemma, suffix = _LEMMATIZE('rolling', Tag.VERB)
        self.assertEqual('roll', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('rolled', Tag.VERB)
        self.assertEqual('roll', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('rolls', Tag.VERB)
        self.assertEqual('roll', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_bark(self):
        lemma, suffix = _LEMMATIZE('barking', Tag.VERB)
        self.assertEqual('bark', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('barked', Tag.VERB)
        self.assertEqual('bark', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('barks', Tag.VERB)
        self.assertEqual('bark', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_bake(self):
        lemma, suffix = _LEMMATIZE('baking', Tag.VERB)
        self.assertEqual('bake', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('baked', Tag.VERB)
        self.assertEqual('bake', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('bakes', Tag.VERB)
        self.assertEqual('bake', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_free(self):
        lemma, suffix = _LEMMATIZE('freeing', Tag.VERB)
        self.assertEqual('free', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('freed', Tag.VERB)
        self.assertEqual('free', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('frees', Tag.VERB)
        self.assertEqual('free', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_dye(self):
        lemma, suffix = _LEMMATIZE('dyeing', Tag.VERB)
        self.assertEqual('dye', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('dyed', Tag.VERB)
        self.assertEqual('dye', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('dyes', Tag.VERB)
        self.assertEqual('dye', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_party(self):
        lemma, suffix = _LEMMATIZE('partying', Tag.VERB)
        self.assertEqual('party', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('partied', Tag.VERB)
        self.assertEqual('party', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('parties', Tag.VERB)
        self.assertEqual('party', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_tiptoe(self):
        lemma, suffix = _LEMMATIZE('tiptoeing', Tag.VERB)
        self.assertEqual('tiptoe', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('tiptoed', Tag.VERB)
        self.assertEqual('tiptoe', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('tiptoes', Tag.VERB)
        self.assertEqual('tiptoe', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_boycott(self):
        lemma, suffix = _LEMMATIZE('boycotting', Tag.VERB)
        self.assertEqual('boycott', lemma)
        self.assertEqual(Suffix.PROGRESSIVE, suffix)

        lemma, suffix = _LEMMATIZE('boycotted', Tag.VERB)
        self.assertEqual('boycott', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('boycotts', Tag.VERB)
        self.assertEqual('boycott', lemma)
        self.assertEqual(Suffix.THIRD_PERSON, suffix)

    def test_verb_break(self):
        lemma, suffix = _LEMMATIZE('broke', Tag.VERB)
        self.assertEqual('break', lemma)
        self.assertEqual(Suffix.PAST, suffix)

        lemma, suffix = _LEMMATIZE('broken', Tag.VERB)
        self.assertEqual('break', lemma)
        self.assertEqual(Suffix.PAST, suffix)

    def test_verb_need(self):
        lemma, suffix = _LEMMATIZE('need', Tag.VERB)
        self.assertEqual('need', lemma)
        self.assertEqual(None, suffix)

    # ADJECTIVES
    # -------------------------------------------------------------------------->

    def test_adj_fat(self):
        lemma, suffix = _LEMMATIZE('fattest', Tag.ADJ)
        self.assertEqual('fat', lemma)
        self.assertEqual(Suffix.SUPERLATIVE, suffix)

        lemma, suffix = _LEMMATIZE('fatter', Tag.ADJ)
        self.assertEqual('fat', lemma)
        self.assertEqual(Suffix.COMPARATIVE, suffix)

    def test_adj_tall(self):
        lemma, suffix = _LEMMATIZE('tallest', Tag.ADJ)
        self.assertEqual('tall', lemma)
        self.assertEqual(Suffix.SUPERLATIVE, suffix)

        lemma, suffix = _LEMMATIZE('taller', Tag.ADJ)
        self.assertEqual('tall', lemma)
        self.assertEqual(Suffix.COMPARATIVE, suffix)

    def test_adj_happy(self):
        lemma, suffix = _LEMMATIZE('happiest', Tag.ADJ)
        self.assertEqual('happy', lemma)
        self.assertEqual(Suffix.SUPERLATIVE, suffix)

        lemma, suffix = _LEMMATIZE('happier', Tag.ADJ)
        self.assertEqual('happy', lemma)
        self.assertEqual(Suffix.COMPARATIVE, suffix)

    def test_adj_large(self):
        lemma, suffix = _LEMMATIZE('largest', Tag.ADJ)
        self.assertEqual('large', lemma)
        self.assertEqual(Suffix.SUPERLATIVE, suffix)

        lemma, suffix = _LEMMATIZE('larger', Tag.ADJ)
        self.assertEqual('large', lemma)
        self.assertEqual(Suffix.COMPARATIVE, suffix)

    def test_adj_round(self):
        lemma, suffix = _LEMMATIZE('roundest', Tag.ADJ)
        self.assertEqual('round', lemma)
        self.assertEqual(Suffix.SUPERLATIVE, suffix)

        lemma, suffix = _LEMMATIZE('rounder', Tag.ADJ)
        self.assertEqual('round', lemma)
        self.assertEqual(Suffix.COMPARATIVE, suffix)

    def test_adj_free(self):
        lemma, suffix = _LEMMATIZE('freest', Tag.ADJ)
        self.assertEqual('free', lemma)
        self.assertEqual(Suffix.SUPERLATIVE, suffix)

        lemma, suffix = _LEMMATIZE('freer', Tag.ADJ)
        self.assertEqual('free', lemma)
        self.assertEqual(Suffix.COMPARATIVE, suffix)

    def test_adj_bad(self):
        lemma, suffix = _LEMMATIZE('worst', Tag.ADJ)
        self.assertEqual('bad', lemma)
        self.assertEqual(Suffix.SUPERLATIVE, suffix)

        lemma, suffix = _LEMMATIZE('worse', Tag.ADJ)
        self.assertEqual('bad', lemma)
        self.assertEqual(Suffix.COMPARATIVE, suffix)

    def test_adj_sober(self):
        lemma, suffix = _LEMMATIZE('sober', Tag.ADJ)
        self.assertEqual('sober', lemma)
        self.assertEqual(None, suffix)

    # NOUNS
    # -------------------------------------------------------------------------->

    def test_noun_thief(self):
        lemma, suffix = _LEMMATIZE('thieves', Tag.NOUN)
        self.assertEqual('thief', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_knife(self):
        lemma, suffix = _LEMMATIZE('knives', Tag.NOUN)
        self.assertEqual('knife', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_hive(self):
        lemma, suffix = _LEMMATIZE('hives', Tag.NOUN)
        self.assertEqual('hive', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_calf(self):
        lemma, suffix = _LEMMATIZE('calves', Tag.NOUN)
        self.assertEqual('calf', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_berry(self):
        lemma, suffix = _LEMMATIZE('berries', Tag.NOUN)
        self.assertEqual('berry', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_lie(self):
        lemma, suffix = _LEMMATIZE('lies', Tag.NOUN)
        self.assertEqual('lie', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_fox(self):
        lemma, suffix = _LEMMATIZE('foxes', Tag.NOUN)
        self.assertEqual('fox', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_axe(self):
        lemma, suffix = _LEMMATIZE('axes', Tag.NOUN)
        self.assertEqual('axe', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_gamer(self):
        lemma, suffix = _LEMMATIZE('gamers', Tag.NOUN)
        self.assertEqual('gamer', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_woman(self):
        lemma, suffix = _LEMMATIZE('women', Tag.NOUN)
        self.assertEqual('woman', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_hero(self):
        lemma, suffix = _LEMMATIZE('heroes', Tag.NOUN)
        self.assertEqual('hero', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_child(self):
        lemma, suffix = _LEMMATIZE('children', Tag.NOUN)
        self.assertEqual('child', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

        lemma, suffix = _LEMMATIZE('grand-children', Tag.NOUN)
        self.assertEqual('grand-child', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

        lemma, suffix = _LEMMATIZE('grandchildren', Tag.NOUN)
        self.assertEqual('grandchild', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_acumen(self):
        lemma, suffix = _LEMMATIZE('acumen', Tag.NOUN)
        self.assertEqual('acumen', lemma)
        self.assertEqual(None, suffix)

    def test_noun_criterion(self):
        lemma, suffix = _LEMMATIZE('criteria', Tag.NOUN)
        self.assertEqual('criterion', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

        lemma, suffix = _LEMMATIZE('sub-criteria', Tag.NOUN)
        self.assertEqual('sub-criterion', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

        lemma, suffix = _LEMMATIZE('subcriteria', Tag.NOUN)
        self.assertEqual('subcriterion', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_phenomenon(self):
        lemma, suffix = _LEMMATIZE('phenomena', Tag.NOUN)
        self.assertEqual('phenomenon', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_analysis(self):
        lemma, suffix = _LEMMATIZE('analyses', Tag.NOUN)
        self.assertEqual('analysis', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_fungus(self):
        lemma, suffix = _LEMMATIZE('fungi', Tag.NOUN)
        self.assertEqual('fungus', lemma)
        self.assertEqual(Suffix.PLURAL, suffix)

    def test_noun_business(self):
        lemma, suffix = _LEMMATIZE('business', Tag.NOUN)
        self.assertEqual('business', lemma)
        self.assertEqual(None, suffix)

    def test_noun_caucus(self):
        lemma, suffix = _LEMMATIZE('caucus', Tag.NOUN)
        self.assertEqual('caucus', lemma)
        self.assertEqual(None, suffix)

    def test_noun_metamorphosis(self):
        lemma, suffix = _LEMMATIZE('metamorphosis', Tag.NOUN)
        self.assertEqual('metamorphosis', lemma)
        self.assertEqual(None, suffix)

    # PRONOUNS
    # -------------------------------------------------------------------------->

    def test_pron_us(self):
        lemma, suffix = _LEMMATIZE("'s", Tag.NOUN)
        self.assertEqual('we', lemma)
        self.assertEqual(None, suffix)

        lemma, suffix = _LEMMATIZE("'s", Tag.PRON)
        self.assertEqual('we', lemma)
        self.assertEqual(None, suffix)


if __name__ == '__main__':
    unittest.main()
