import unittest

from scrappybara.langmodel.language_model_builder import ModifiedKneserNeyMinOrderError, LanguageModelBuilder


class TestLanguageModelBuilder(unittest.TestCase):

    # ERRORS
    # -------------------------------------------------------------------------->

    def test_mkn_min_order_error(self):
        self.assertRaises(ModifiedKneserNeyMinOrderError, lambda: LanguageModelBuilder(1))


if __name__ == '__main__':
    unittest.main()
