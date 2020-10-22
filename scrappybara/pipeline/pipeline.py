import sys
import itertools
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf

import scrappybara.config as cfg
from scrappybara.langmodel.language_model import LanguageModel
from scrappybara.pipeline.document import Document
from scrappybara.pipeline.labelled_sentence_pipeline import LabelledSentencePipeline
from scrappybara.preprocessing.sentencizer import Sentencizer
from scrappybara.syntax.parser import Parser
from scrappybara.semantics.entity_linker import EntityLinker, extract_lexeme_bag
from scrappybara.utils.multithreading import run_multithreads
from scrappybara.utils.files import txt_file_reader


class Pipeline(LabelledSentencePipeline):
    # Used to split sentences again after they've been sentencized once
    __splitters = {':', '"', ';', '(', ')', '[', ']', '{', '}', '-'}

    def __init__(self, gpu_batch_size=-1):
        # Check data versioning
        with txt_file_reader('version.txt') as txt_file:
            version = txt_file.read()
        if version != cfg.DATA_VERSION:
            sys.exit('Wrong version of data: need to run "python -m scrappybara download".')
        # GPU ?
        self.__gpu_batch_size = gpu_batch_size
        # Language model
        self.__lm = LanguageModel()
        super().__init__(self.__lm)
        # Sentencizer
        self.__sentencize = Sentencizer()
        # Parser
        if gpu_batch_size > 0:
            self.__parse = Parser(self.__lm, gpu_batch_size)
        else:
            with tf.device('/CPU:0'):
                self.__parse = Parser(self.__lm, 128)
        # Entity linker
        self.__link_entities = EntityLinker()

    def __call__(self, texts):
        """Processes all texts in memory & returns a list of documents"""
        tokens, sent_ranges = self.__extract_sentences(texts)
        # Run pipeline on GPU or CPU
        if self.__gpu_batch_size > 0:
            _, node_trees, node_dicts = self.__process_tokens(tokens)
        else:
            with tf.device('/CPU:0'):
                _, node_trees, node_dicts = self.__process_tokens(tokens)
        # Create documents
        docs = []
        for idx, start_end in enumerate(sent_ranges):
            start, end = start_end
            # Link resources
            nodes = [node for node_dict in node_dicts[start:end] for node in node_dict.values()]
            entities = self.__link_entities(nodes, texts[idx])
            docs.append(Document(entities))
        return docs

    def __extract_sentences(self, texts):
        """Returns a flat list of sentences from all texts.
        Also returns sentences' ranges to be able to regroup by text later.
        """
        # Text tokens is a list of list of list of tokens (tokens grouped by sentences for each text)
        tokens = run_multithreads(texts, self.__sentencize, cfg.NB_PROCESSES)
        tokens = run_multithreads(tokens, self.__shorten_sentences, cfg.NB_PROCESSES)
        # Remember the association text/sentences
        sent_ranges = []
        total_sents = 0
        for token_lists in tokens:
            new_total = total_sents + len(token_lists)
            sent_ranges.append((total_sents, new_total))
            total_sents = new_total
        return [token_lists for group in tokens for token_lists in group], sent_ranges

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

    def __process_tokens(self, token_lists):
        """Proxy for both production __call__ and testing"""
        tags, node_trees = self.__parse(token_lists)
        sent_packs = list(zip(token_lists, tags, node_trees))
        node_dicts = run_multithreads(sent_packs, self._process_sentence, cfg.NB_PROCESSES)
        return tags, node_trees, node_dicts

    # INTERNAL USE
    # -------------------------------------------------------------------------->

    def _extract_lexeme_bags(self, texts):
        tokens, sent_ranges = self.__extract_sentences(texts)
        _, _, node_dicts = self.__process_tokens(tokens)
        lexeme_bags = []
        for start, end in sent_ranges:
            nodes = [node for node_dict in node_dicts[start:end] for node in node_dict.values()]
            lexeme_bags.append(extract_lexeme_bag(nodes))
        return lexeme_bags

    def _test_parse(self, input_sentence):
        """Parses a single sentence.
        Arg input_sentence can be a string or a list of tokens"""
        if isinstance(input_sentence, list):
            tokens = [input_sentence]
        else:
            tokens = self.__sentencize(input_sentence)
        tags, trees, node_dicts = self.__process_tokens(tokens)
        return tokens[0], tags[0], trees[0], node_dicts[0]

    def _test_process(self, text):
        """To debug every step, except semantics"""
        token_lists = self.__sentencize(text)
        tags, trees, node_dicts = self.__process_tokens(token_lists)
        return token_lists[0], tags[0], trees[0], node_dicts[0]
