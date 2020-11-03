import sys

import scrappybara.config as cfg
from scrappybara.pipeline.document import Document
from scrappybara.pipeline.parsing_pipeline import ParsingPipeline
from scrappybara.pipeline.sentence import Sentence
from scrappybara.semantics.entity_linker import EntityLinker
from scrappybara.utils.files import txt_file_reader, load_pkl_file
from scrappybara.utils.multithreading import run_multithreads


class Pipeline(ParsingPipeline):
    """Production pipeline"""

    def __init__(self, batch_size=128):
        # Check data versioning
        with txt_file_reader(cfg.DATA_DIR / 'version.txt') as txt_file:
            if txt_file.read() != cfg.DATA_VERSION:
                sys.exit('Wrong data version. Please download again: "python3 -m scrappybara download".')
        super().__init__(batch_size)
        # Load data
        self.__feature_idx_idf = load_pkl_file(cfg.DATA_DIR / 'entities' / 'feature_idx_idf.pkl')
        form_eids = load_pkl_file(cfg.DATA_DIR / 'entities' / 'form_eids.pkl')
        eid_vector = load_pkl_file(cfg.DATA_DIR / 'entities' / 'eid_vector.pkl')
        # Pipeline
        self.__link_entities = EntityLinker(form_eids, eid_vector)

    def __call__(self, texts):
        """Processes all texts in memory & returns a list of documents"""
        token_lists, sent_ranges = self._extract_sentences(texts)
        standard_lists = run_multithreads(token_lists, self._standardize, cfg.NB_PROCESSES)
        _, _, node_dicts, node_trees = self._parse_tokens(token_lists, standard_lists)
        # Create documents
        docs = []
        for start, end in sent_ranges:
            doc_node_dicts = node_dicts[start:end]
            doc_node_trees = node_trees[start:end]
            sentences = []
            # Link entities
            vector = self._vectorize(doc_node_dicts)
            for idx, doc_node_dict in enumerate(doc_node_dicts):
                entities = self.__link_entities(doc_node_dict, doc_node_trees[idx], vector)
                sentences.append(Sentence(entities))
            docs.append(Document(sentences))
        return docs

    def _vectorize(self, node_dicts):
        """Returns sparse vector of a text.
        A node_dict represents a sentence.
        """
        lemma_tag_list = [(node.lemma, node.tag) for node_dict in node_dicts for node in node_dict.values()]
        lexeme_counter = self._count_lexemes(lemma_tag_list)
        total_count = sum(lexeme_counter.values())
        vector = {}  # idx of lexeme => score tf.idf
        for lexeme, count in lexeme_counter.items():
            if lexeme in self.__feature_idx_idf:
                idx, idf = self.__feature_idx_idf[lexeme]
                vector[idx] = (count / total_count) * idf
        return vector
