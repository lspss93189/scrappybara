import collections
import itertools
import sys

import scrappybara.config as cfg
from scrappybara.langmodel.language_model import LanguageModel
from scrappybara.pipeline.document import Document
from scrappybara.pipeline.labelled_sentence_pipeline import LabelledSentencePipeline
from scrappybara.pipeline.sentence import Sentence
from scrappybara.preprocessing.sentencizer import Sentencizer
from scrappybara.semantics.entity_linker import EntityLinker
from scrappybara.syntax.charset import Charset
from scrappybara.syntax.models import PDepsModel, TransModel, PTagsModel
from scrappybara.syntax.parser import Parser
from scrappybara.syntax.tags import Tag
from scrappybara.syntax.wordset import Wordset
from scrappybara.utils.files import txt_file_reader, load_pkl_file
from scrappybara.utils.multithreading import run_multithreads


class Pipeline(LabelledSentencePipeline):
    """Production pipeline"""

    # Used to split sentences again after they've been sentencized once
    __splitters = {':', '"', ';', '(', ')', '[', ']', '{', '}', '—'}

    # Lexeme's tags
    __lex_tags = {Tag.NOUN, Tag.PROPN, Tag.ADJ, Tag.VERB}

    def __init__(self, batch_size=128):
        # Check data versioning
        with txt_file_reader(cfg.DATA_DIR / 'version.txt') as txt_file:
            version = txt_file.read()
        if version != cfg.DATA_VERSION:
            sys.exit('Wrong data version. Please download again: "python3 -m scrappybara download".')
        # Load data
        lm = LanguageModel()
        super().__init__(lm)
        self.__lexeme_idx_idf = load_pkl_file(cfg.DATA_DIR / 'entities' / 'lexemes.pkl')  # lexeme => (idx, idf score)
        self._charset = Charset().load()
        self._wordset = Wordset(lm).load()
        self._ptags_model = PTagsModel(len(self._charset)).load()
        pdeps_model = PDepsModel(len(self._charset)).load()
        trans_model = TransModel(len(self._charset)).load()
        form_eids = load_pkl_file(cfg.DATA_DIR / 'entities' / 'form_eids.pkl')  # form => list of entity ids
        eid_vector = load_pkl_file(cfg.DATA_DIR / 'entities' / 'eid_vector.pkl')  # eID => dict sparce vector
        # Pipeline
        self._sentencize = Sentencizer()
        self.__parse = Parser(self._charset, self._wordset, self._ptags_model, pdeps_model, trans_model, batch_size)
        self.__link_entities = EntityLinker(form_eids, eid_vector)

    def __call__(self, texts):
        """Processes all texts in memory & returns a list of documents"""
        tokens, sent_ranges = self._extract_sentences(texts)
        _, _, node_dicts, node_trees = self._parse_tokens(tokens)
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

    def __shorten_sentences(self, token_lists):
        """Resplit a text's sentences that are too long"""
        new_token_lists = []
        for tokens in token_lists:
            if len(tokens) > cfg.MAX_SENT_LENGTH:
                new_token_lists.extend(
                    [list(group) for b, group in itertools.groupby(tokens, lambda x: x in self.__splitters) if not b])
            else:
                new_token_lists.append(tokens)
        # Remove sentences that are still too long
        return [tokens for tokens in new_token_lists if len(tokens) <= cfg.MAX_SENT_LENGTH]

    def _extract_sentences(self, texts):
        """Returns a flat list of sentences from all texts.
        Also returns sentences' ranges to be able to regroup by text later.
        """
        # Text tokens is a list of list of list of tokens (tokens grouped by sentences for each text)
        tokens = run_multithreads(texts, self._sentencize, cfg.NB_PROCESSES)
        tokens = run_multithreads(tokens, self.__shorten_sentences, cfg.NB_PROCESSES)
        # Remember the association text/sentences
        sent_ranges = []
        total_sents = 0
        for token_lists in tokens:
            new_total = total_sents + len(token_lists)
            sent_ranges.append((total_sents, new_total))
            total_sents = new_total
        return [token_lists for group in tokens for token_lists in group], sent_ranges

    def _parse_tokens(self, token_lists):
        """Parses multiple sentences"""
        tags, idx_trees = self.__parse(token_lists)
        sent_packs = list(zip(token_lists, tags, idx_trees))
        node_dict_node_tree_list = run_multithreads(sent_packs, self._process_sentence, cfg.NB_PROCESSES)
        node_dicts, node_trees = zip(*node_dict_node_tree_list)
        return tags, idx_trees, node_dicts, node_trees

    def _count_lexemes(self, lemma_tag_list):
        """Counts lemmas with an appropriate tag"""
        lexemes = [lemma for lemma, tag in lemma_tag_list if tag in self.__lex_tags]
        return collections.Counter(lexemes)

    def _vectorize(self, node_dicts):
        """Returns sparse vector of a text.
        A node_dict represents a sentence.
        """
        lemma_tag_list = [(node.lemma, node.tag) for node_dict in node_dicts for node in node_dict.values()]
        lexeme_counter = self._count_lexemes(lemma_tag_list)
        total_count = sum(lexeme_counter.values())
        vector = {}  # idx of lexeme => score tf.idf
        for lexeme, count in lexeme_counter.items():
            if lexeme in self.__lexeme_idx_idf:
                idx, idf = self.__lexeme_idx_idf[lexeme]
                vector[idx] = (count / total_count) * idf
        return vector
