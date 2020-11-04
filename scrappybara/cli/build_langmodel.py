import re

from lxml import etree

import scrappybara.config as cfg
from scrappybara.langmodel.language_model_builder import LanguageModelBuilder


class _Sanitizer(object):
    __re_replacements = [
        # Diaeresis
        (re.compile(r'eë'), 'ee'),
        (re.compile(r'oö'), 'oo'),
    ]

    def __call__(self, text):
        text = text.strip()
        for rep in self.__re_replacements:
            text = re.sub(rep[0], rep[1], text)
        return ' '.join(text.split())


def build_langmodel(resource_dir):
    """Builds language model for Scrappybara's pipeline"""
    max_order = 2
    # Read articles
    sanitize = _Sanitizer()
    root = etree.parse(resource_dir + '/corpus.xml').getroot()
    texts = [sanitize(child.text) for article in root for child in article if child.tag == 'body']
    # Build LM
    build_lm = LanguageModelBuilder(max_order, 'modified_kneser_ney', cfg.DATA_DIR / 'langmodel')
    build_lm(iter(texts))


build_langmodel('/media/data/scrappybara')
