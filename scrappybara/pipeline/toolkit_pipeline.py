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
        tag_lists = self.__tag(token_lists)
        doc_packs = []
        for start, end in sent_ranges:
            tokens = [token for token_list in token_lists[start:end] for token in token_list]
            tags = [tag for tag_list in tag_lists[start:end] for tag in tag_list]
            doc_packs.append((tokens, tags))
        return run_multithreads(doc_packs, self._count_doc_lexemes, cfg.NB_PROCESSES)

    def _count_doc_lexemes(self, doc_pack):
        """A multithreaded process to count lexemes in a single doc"""
        tokens, tags = doc_pack
        lemma_tag_list = [(self._lemmatize(token, tag)[0], tag) for token, tag in zip(tokens, tags)]
        return self._count_lexemes(lemma_tag_list)
