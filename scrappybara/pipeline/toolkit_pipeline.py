import scrappybara.config as cfg
from scrappybara.pipeline.parsing_pipeline import ParsingPipeline
from scrappybara.syntax.tagger import Tagger
from scrappybara.utils.multithreading import run_multithreads


class LexemePipeline(ParsingPipeline):
    """Extracts lexeme bags from raw texts"""

    def __init__(self, batch_size=128):
        super().__init__(batch_size)
        self.__tag = Tagger(self._charset, self._wordset, self._ptags_model, batch_size)

    def __call__(self, texts):
        """Processes all texts in memory & returns a list of lexeme bags"""
        token_lists, sent_ranges = self._extract_sentences(texts)
        standard_lists = run_multithreads(token_lists, self._standardize, cfg.NB_PROCESSES)
        tag_lists = self.__tag(token_lists, standard_lists)
        doc_packs = []
        for start, end in sent_ranges:
            standards = [standard for standard_list in standard_lists[start:end] for standard in standard_list]
            tags = [tag for tag_list in tag_lists[start:end] for tag in tag_list]
            doc_packs.append((standards, tags))
        return run_multithreads(doc_packs, self._count_doc_lexemes, cfg.NB_PROCESSES)

    def _count_doc_lexemes(self, doc_pack):
        """Multithreaded process that counts lexemes in a single doc"""
        standards, tags = doc_pack
        lemma_tag_list = [(self._lemmatize(standard, tag)[0], tag) for standard, tag in zip(standards, tags)]
        return self._count_lexemes(lemma_tag_list)
