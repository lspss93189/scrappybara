import unittest

from scrappybara.langmodel.token_context import TokenContext


class TestTokenContext(unittest.TestCase):

    def test_1(self):
        tc = TokenContext('F3', ['L1', 'L2'], ['R4', 'R5'])
        self.assertRaises(Exception, lambda: tc.candidates(1))
        self.assertListEqual(['L1 L2 F3', 'L2 F3 R4', 'F3 R4 R5'], tc.candidates(3))
        self.assertListEqual(['L2 F3', 'F3 R4'], tc.candidates(2))

    def test_2(self):
        tc = TokenContext('F3', ['L1', 'L2'], ['R4'])
        self.assertListEqual(['L1 L2 F3', 'L2 F3 R4'], tc.candidates(3))
        self.assertListEqual(['L2 F3', 'F3 R4'], tc.candidates(2))

    def test_3(self):
        tc = TokenContext('F3', ['L2'], ['R4'])
        self.assertListEqual(['L2 F3 R4'], tc.candidates(3))
        self.assertListEqual(['L2 F3', 'F3 R4'], tc.candidates(2))

    def test_4(self):
        tc = TokenContext('F3', [], [])
        self.assertListEqual([], tc.candidates(3))
        self.assertListEqual([], tc.candidates(2))


if __name__ == '__main__':
    unittest.main()
