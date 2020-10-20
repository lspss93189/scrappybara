import unittest

from scrappybara.langmodel.mkn_smoother import MKNSmoother
from scrappybara.langmodel.ngram_store import NgramStore
from scrappybara.langmodel.ngrams_extraction import extract_ngrams


class TestMKNSmoother(unittest.TestCase):

    def test_small_corpus(self):
        text_1 = 'this is a list containing the tallest buildings in blobby land .'
        text_2 = 'the classic pyramid is the tallest building in blobby land .'
        text_3 = 'the classic hotel is the tallest tower in blobby land .'
        text_4 = 'the classic tower is the lowest tower in blobby land .'
        text_5 = 'the pyramid is the tallest tower in blobby !'
        text_6 = 'this is the classic pyramid .'
        text_7 = 'this is a hotel list .'

        texts = [text_1, text_2, text_3, text_4, text_5, text_6, text_7]
        store = NgramStore()

        for text in texts:
            [store.make_ngram(ngram) for ngram in extract_ngrams([text.split()], 1)]
            [store.make_ngram(ngram) for ngram in extract_ngrams([text.split()], 2)]
            [store.make_ngram(ngram) for ngram in extract_ngrams([text.split()], 3)]

        smoother = MKNSmoother(store.ngrams, 3, 1)

        # For order 1, no discount
        self.assertRaises(KeyError, lambda: smoother.discount_1(1))
        self.assertRaises(KeyError, lambda: smoother.discount_2(1))
        self.assertRaises(KeyError, lambda: smoother.discount_3(1))

        # For order 2
        self.assertAlmostEqual(0.6666666667, smoother.discount_1(2))
        self.assertAlmostEqual(1.0000000000, smoother.discount_2(2))
        self.assertAlmostEqual(-1.0000000000, smoother.discount_3(2))

        # For order 3
        self.assertAlmostEqual(0.7142857143, smoother.discount_1(3))
        self.assertAlmostEqual(1.142857143, smoother.discount_2(3))
        self.assertAlmostEqual(1.571428571, smoother.discount_3(3))

        # Calculate
        uni_results = smoother.calc_unigram_probas()
        bi_results = smoother.calc_higher_order_probas(2)
        tri_results = smoother.calc_higher_order_probas(3)

        # Ngrams results all correct size
        self.assertEqual(17, len(uni_results))
        self.assertEqual(27, len(bi_results))
        self.assertEqual(33, len(tri_results))

        probas_dict = {1: uni_results, 2: bi_results, 3: tri_results}

        # Order 1
        index = -1
        for ngram in smoother.ngrams(1):
            index += 1
            mkn = probas_dict[1][index]
            if ngram.text == 'the':
                self.assertAlmostEqual(0.074074074, mkn)
            if ngram.text == 'is':
                self.assertAlmostEqual(0.148148148, mkn)
            if ngram.text == 'in':
                self.assertAlmostEqual(0.111111111, mkn)
            if ngram.text == 'blobby':
                self.assertAlmostEqual(0.037037037, mkn)
            if ngram.text == 'tallest':
                self.assertAlmostEqual(0.037037037, mkn)
            if ngram.text == 'land':
                self.assertAlmostEqual(0.037037037, mkn)
            if ngram.text == 'classic':
                self.assertAlmostEqual(0.037037037, mkn)
            if ngram.text == 'tower':
                self.assertAlmostEqual(0.111111111, mkn)
            if ngram.text == 'this':
                self.assertAlmostEqual(0.0, mkn)
            if ngram.text == 'pyramid':
                self.assertAlmostEqual(0.074074074, mkn)
            if ngram.text == 'a':
                self.assertAlmostEqual(0.037037037, mkn)
            if ngram.text == 'list':
                self.assertAlmostEqual(0.074074074, mkn)
            if ngram.text == 'hotel':
                self.assertAlmostEqual(0.074074074, mkn)
            if ngram.text == 'containing':
                self.assertAlmostEqual(0.037037037, mkn)
            if ngram.text == 'buildings':
                self.assertAlmostEqual(0.037037037, mkn)
            if ngram.text == 'building':
                self.assertAlmostEqual(0.037037037, mkn)
            if ngram.text == 'lowest':
                self.assertAlmostEqual(0.037037037, mkn)

        # Order 2
        index = -1
        for ngram in smoother.ngrams(2):
            index += 1
            mkn = probas_dict[2][index]
            if ngram.text == 'in blobby':
                self.assertAlmostEqual(1.19259259, mkn)
            if ngram.text == 'is the':
                self.assertAlmostEqual(0.85714286, mkn)
            if ngram.text == 'the tallest':
                self.assertAlmostEqual(0.49753086, mkn)
            if ngram.text == 'blobby land':
                self.assertAlmostEqual(0.99259259, mkn)
            if ngram.text == 'the classic':
                self.assertAlmostEqual(0.49753086, mkn)
            if ngram.text == 'this is':
                self.assertAlmostEqual(1.28395062, mkn)
            if ngram.text == 'tower in':
                self.assertAlmostEqual(0.99074074, mkn)
            if ngram.text == 'is a':
                self.assertAlmostEqual(0.14285714, mkn)
            if ngram.text == 'classic pyramid':
                self.assertAlmostEqual(0.29320988, mkn)
            if ngram.text == 'pyramid is':
                self.assertAlmostEqual(0.38271605, mkn)
            if ngram.text == 'tallest tower':
                self.assertAlmostEqual(0.31481481, mkn)
            if ngram.text == 'a list':
                self.assertAlmostEqual(0.21604938, mkn)
            if ngram.text == 'list containing':
                self.assertAlmostEqual(0.17901235, mkn)
            if ngram.text == 'containing the':
                self.assertAlmostEqual(0.38271605, mkn)
            if ngram.text == 'tallest buildings':
                self.assertAlmostEqual(0.10493827, mkn)
            if ngram.text == 'buildings in':
                self.assertAlmostEqual(0.40740741, mkn)
            if ngram.text == 'tallest building':
                self.assertAlmostEqual(0.10493827, mkn)
            if ngram.text == 'building in':
                self.assertAlmostEqual(0.40740741, mkn)
            if ngram.text == 'classic hotel':
                self.assertAlmostEqual(0.12654321, mkn)
            if ngram.text == 'hotel is':
                self.assertAlmostEqual(0.26543210, mkn)
            if ngram.text == 'classic tower':
                self.assertAlmostEqual(0.14814815, mkn)
            if ngram.text == 'tower is':
                self.assertAlmostEqual(0.07098765, mkn)
            if ngram.text == 'the lowest':
                self.assertAlmostEqual(0.03086420, mkn)
            if ngram.text == 'lowest tower':
                self.assertAlmostEqual(0.40740741, mkn)
            if ngram.text == 'the pyramid':
                self.assertAlmostEqual(0.02839506, mkn)
            if ngram.text == 'a hotel':
                self.assertAlmostEqual(0.21604938, mkn)
            if ngram.text == 'hotel list':
                self.assertAlmostEqual(0.21604938, mkn)

        # Order 3
        index = -1
        for ngram in smoother.ngrams(3):
            index += 1
            mkn = probas_dict[3][index]
            if ngram.text == 'in blobby land':
                self.assertAlmostEqual(0.56386999, mkn)
            if ngram.text == 'is the tallest':
                self.assertAlmostEqual(0.41058201, mkn)
            if ngram.text == 'tower in blobby':
                self.assertAlmostEqual(0.71915680, mkn)
            if ngram.text == 'this is a':
                self.assertAlmostEqual(0.32108844, mkn)
            if ngram.text == 'the classic pyramid':
                self.assertAlmostEqual(0.31254724, mkn)
            if ngram.text == 'pyramid is the':
                self.assertAlmostEqual(0.70612245, mkn)
            if ngram.text == 'the tallest tower':
                self.assertAlmostEqual(0.33106576, mkn)
            if ngram.text == 'tallest tower in':
                self.assertAlmostEqual(0.58478206, mkn)
            if ngram.text == 'is a list':
                self.assertAlmostEqual(0.28017133, mkn)
            if ngram.text == 'a list containing':
                self.assertAlmostEqual(0.50743260, mkn)
            if ngram.text == 'list containing the':
                self.assertAlmostEqual(0.52506929, mkn)
            if ngram.text == 'containing the tallest':
                self.assertAlmostEqual(0.43436634, mkn)
            if ngram.text == 'the tallest buildings':
                self.assertAlmostEqual(0.15117158, mkn)
            if ngram.text == 'tallest buildings in':
                self.assertAlmostEqual(0.54270597, mkn)
            if ngram.text == 'buildings in blobby':
                self.assertAlmostEqual(0.61703200, mkn)
            if ngram.text == 'classic pyramid is':
                self.assertAlmostEqual(0.32237339, mkn)
            if ngram.text == 'the tallest building':
                self.assertAlmostEqual(0.15117158, mkn)
            if ngram.text == 'tallest building in':
                self.assertAlmostEqual(0.54270597, mkn)
            if ngram.text == 'building in blobby':
                self.assertAlmostEqual(0.61703200, mkn)
            if ngram.text == 'the classic hotel':
                self.assertAlmostEqual(0.16969010, mkn)
            if ngram.text == 'classic hotel is':
                self.assertAlmostEqual(0.45830184, mkn)
            if ngram.text == 'hotel is the':
                self.assertAlmostEqual(0.63265306, mkn)
            if ngram.text == 'the classic tower':
                self.assertAlmostEqual(0.18820862, mkn)
            if ngram.text == 'classic tower is':
                self.assertAlmostEqual(0.34198371, mkn)
            if ngram.text == 'tower is the':
                self.assertAlmostEqual(0.63265306, mkn)
            if ngram.text == 'is the lowest':
                self.assertAlmostEqual(0.09629630, mkn)
            if ngram.text == 'the lowest tower':
                self.assertAlmostEqual(0.54270597, mkn)
            if ngram.text == 'lowest tower in':
                self.assertAlmostEqual(0.48097758, mkn)
            if ngram.text == 'the pyramid is':
                self.assertAlmostEqual(0.64474679, mkn)
            if ngram.text == 'this is the':
                self.assertAlmostEqual(0.39591837, mkn)
            if ngram.text == 'is the classic':
                self.assertAlmostEqual(0.09629630, mkn)
            if ngram.text == 'is a hotel':
                self.assertAlmostEqual(0.28017133, mkn)
            if ngram.text == 'a hotel list':
                self.assertAlmostEqual(0.42302847, mkn)


if __name__ == '__main__':
    unittest.main()
