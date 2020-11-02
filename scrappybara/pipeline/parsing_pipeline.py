import collections
import itertools

import scrappybara.config as cfg
from scrappybara.langmodel.language_model import LanguageModel
from scrappybara.pipeline.labelled_sentence_pipeline import LabelledSentencePipeline
from scrappybara.preprocessing.sentencizer import Sentencizer
from scrappybara.syntax.charset import Charset
from scrappybara.syntax.models import PDepsModel, TransModel, PTagsModel
from scrappybara.syntax.parser import Parser
from scrappybara.syntax.tags import Tag
from scrappybara.syntax.wordset import Wordset
from scrappybara.utils.multithreading import run_multithreads


class ParsingPipeline(LabelledSentencePipeline):
    """Provides tools necessary to parse raw text, and few other goodies"""

    __lexeme_tags = {Tag.NOUN, Tag.PROPN, Tag.ADJ, Tag.VERB}
    __splitters = {':', '"', ';', '(', ')', '[', ']', '{', '}', '—'}  # Used to split sentences again

    def __init__(self, batch_size=128):
        lm = LanguageModel()
        super().__init__(lm)
        # Load data
        self._charset = Charset().load()
        self._wordset = Wordset(lm).load()
        self._ptags_model = PTagsModel(len(self._charset)).load()
        pdeps_model = PDepsModel(len(self._charset)).load()
        trans_model = TransModel(len(self._charset)).load()
        # Pipeline
        self._sentencize = Sentencizer()
        self.__parse = Parser(self._charset, self._wordset, self._ptags_model, pdeps_model, trans_model, batch_size)

    def __call__(self, input_sentence):
        """Parses a single sentence.
        Arg input_sentence can be a string or a list of tokens.
        """
        if isinstance(input_sentence, list):
            tokens = [input_sentence]
        else:
            tokens = self._sentencize(input_sentence)
        tags, idx_trees, node_dicts, _ = self._parse_tokens(tokens)
        return tokens[0], tags[0], idx_trees[0], node_dicts[0]

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
        lexemes = [lemma for lemma, tag in lemma_tag_list if tag in self.__lexeme_tags]
        return collections.Counter(lexemes)
