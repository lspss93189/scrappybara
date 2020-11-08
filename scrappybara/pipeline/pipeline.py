import sys

import scrappybara.config as cfg
from scrappybara.pipeline.document import Document
from scrappybara.pipeline.lexeme_pipeline import LexemePipeline
from scrappybara.semantics.entity_linker import EntityLinker
from scrappybara.utils.files import txt_file_reader, load_pkl_file
from scrappybara.utils.multithreading import run_multithreads


class Pipeline(LexemePipeline):
    """Production pipeline"""

    def __init__(self, batch_size=128, verbose=True):
        # Check data versioning
        with txt_file_reader(cfg.DATA_DIR / 'version.txt') as txt_file:
            if txt_file.read() != cfg.DATA_VERSION:
                sys.exit('Wrong data version. Please download again: "python3 -m scrappybara download".')
        super().__init__(batch_size, verbose)
        # Load data
        if verbose:
            print('Preparing Entity Linker... ', end='')
        form_eids = load_pkl_file(cfg.DATA_DIR / 'entities' / 'forms.pkl')
        feature_dc = load_pkl_file(cfg.DATA_DIR / 'entities' / 'features.pkl')
        eid_featbag = load_pkl_file(cfg.DATA_DIR / 'entities' / 'bags.pkl')
        constants = load_pkl_file(cfg.DATA_DIR / 'entities' / 'vars.pkl')
        # Pipeline
        self.__link_entities = EntityLinker(form_eids, feature_dc, eid_featbag, constants['total_docs'])
        if verbose:
            print('[DONE]')

    def __call__(self, texts):
        """Processes all texts in memory & returns a list of documents"""
        token_lists, sent_ranges = self._extract_sentences(texts)
        standard_lists = run_multithreads(token_lists, self._standardize, cfg.NB_PROCESSES)
        tag_lists, _, node_dicts, node_trees = self._parse_tokens(token_lists, standard_lists)
        bags = self._extract_lexeme_bags(standard_lists, tag_lists, sent_ranges)
        vectors = run_multithreads(bags, self.__link_entities.vectorize, cfg.NB_PROCESSES)
        entity_lists = self.__link_all_entities(node_dicts, node_trees, sent_ranges, vectors)
        return self.__create_docs(entity_lists, sent_ranges)

    def __link_all_entities(self, node_dicts, node_trees, sent_ranges, vectors):
        """Link entities in every texts, sentence by sentence"""
        sent_packs = []
        for text_idx, start_end in enumerate(sent_ranges):
            for sent_idx in range(*start_end):
                sent_packs.append((node_dicts[sent_idx], node_trees[sent_idx], vectors[text_idx]))
        return run_multithreads(sent_packs, self.__link_entities, cfg.NB_PROCESSES)

    @staticmethod
    def __create_docs(entity_lists, sent_ranges):
        docs = []
        for idx, start_end in enumerate(sent_ranges):
            start, end = start_end
            entities = [entity for entities in entity_lists[start: end] for entity in entities]
            docs.append(Document(entities))
        return docs
