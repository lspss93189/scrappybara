import unittest

from scrappybara.preprocessing.sentencizer import Sentencizer

_SENTENCIZE = Sentencizer()


class TestSentencizer(unittest.TestCase):

    def test_article_with_quotes(self):
        text = "He's breaking records and breaking hearts already: a baby born in Tokyo weighing the same as a large " \
               "onion has gone home healthy, becoming the smallest newborn boy in the world to leave hospital " \
               "safely. And what a cutie this wee one is. The tiny tot weighed just 268 grams — under 10 ounces — " \
               "when he was delivered at 24 weeks, reportedly after he stopped growing in the womb. He was so small " \
               "he fit in an adult's cupped hands. A baby weighing just 268 grams at birth has been released from " \
               "Keio University hospital in Tokyo, after growing to a weight of 3,238 grams, and is believed to be " \
               "the smallest boy in the world to be sent home healthy. But after five months of treatment, he now " \
               "weighs 7.1 pounds, is feeding normally, and has been discharged, Keio University Hospital said. " \
               "\"I can only say I'm happy that he has grown this big because honestly, I wasn't sure he could " \
               "survive,\" the boy's mother said. Doctor Takeshi Arimitsu, who treated the infant, said he wanted to " \
               "tell people that \"there is a possibility that babies will be able to leave the hospital in good " \
               "health even though they are born small.\" Keio University Hospital said the boy was believed to now " \
               "hold the record for the smallest newborn boy to be discharged from a hospital in good health. " \
               "The record was previously held by a boy born in Germany in 2009 weighing just 274 grams, the " \
               "hospital said, citing a registry put together by University of Iowa for the world's tiniest " \
               "surviving babies. The smallest surviving girl was born in Germany in 2015 weighing 252 grams, " \
               "according to the registry. The survival rate of the smallest babies is substantially lower for boys " \
               "compared with girls. Experts are still not entirely sure why, though there have been suggestions it " \
               "could be partly related to the slower development of lungs in male babies, Keio hospital said. " \
               "The baby was discharged last week, two months after his initial due date, local media said. Japan " \
               "has one of the world's lowest rates of infant mortality, according to UNICEF."
        self.assertEqual(16, len(_SENTENCIZE(text)))


if __name__ == '__main__':
    unittest.main()
