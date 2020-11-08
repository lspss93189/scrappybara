import collections

import scrappybara.config as cfg
from scrappybara.pipeline.parsing_pipeline import ParsingPipeline
from scrappybara.syntax.tagger import Tagger
from scrappybara.syntax.tags import LEX_TAGS
from scrappybara.utils.multithreading import run_multithreads


class LexemePipeline(ParsingPipeline):
    """Extracts lexeme bags from raw texts"""

    def __init__(self, batch_size=128, verbose=True):
        super().__init__(batch_size, verbose)
        self.__tag = Tagger(self._charset, self._wordset, self._ptags_model, batch_size)

    def __call__(self, texts):
        """Processes all texts in memory & returns a list of lexeme bags"""
        token_lists, sent_ranges = self._extract_sentences(texts)
        standard_lists = run_multithreads(token_lists, self._standardize, cfg.NB_PROCESSES)
        tag_lists = self.__tag(token_lists, standard_lists)
        return self._extract_lexeme_bags(standard_lists, tag_lists, sent_ranges)

    def __count_text_lexemes(self, standards, tags):
        """Counts lexemes in a single text"""
        lexemes = [(self._lemmatize(standard, tag)[0]) for standard, tag in zip(standards, tags) if tag in LEX_TAGS]
        return collections.Counter(lexemes).most_common()

    def _extract_lexeme_bags(self, standard_lists, tag_lists, sent_ranges):
        """Returns a bag of lexemes (collections.Counter) corresponding to a portion of a text"""
        doc_packs = []
        for start, end in sent_ranges:
            standards = [standard for standard_list in standard_lists[start:end] for standard in standard_list]
            tags = [tag for tag_list in tag_lists[start:end] for tag in tag_list]
            doc_packs.append((standards, tags))
        return run_multithreads(doc_packs, self.__count_text_lexemes, cfg.NB_PROCESSES)
