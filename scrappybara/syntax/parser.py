import collections

import scrappybara.config as cfg
from scrappybara.syntax.charset import Charset
from scrappybara.syntax.dependencies import Dep
from scrappybara.syntax.models import PDepsModel, TransModel
from scrappybara.syntax.models import PTagsModel
from scrappybara.syntax.tags import Tag
from scrappybara.syntax.training_samples import vectorize_sentence, make_masks
from scrappybara.syntax.transitions import Trans
from scrappybara.syntax.wordset import Wordset
from scrappybara.utils.multithreading import run_multithreads
from scrappybara.utils.mutables import make_batches
from scrappybara.utils.tree import Tree


class _Parse(object):
    """Parsing a single sentence"""

    def __init__(self, seq_length, tag_codes, dep_codes, char_codes, word_vectors):
        """Tokens & deps are non-padded"""
        self.__tag_codes = tag_codes
        self.__dep_codes = dep_codes
        self.__char_codes = char_codes
        self.__word_vectors = word_vectors
        self.tags = [Tag(code) for code in tag_codes[1:seq_length - 1]]
        self.__deps = [Dep(code) for code in dep_codes[1:seq_length - 1]]
        self.__buffer = collections.deque([idx for idx in range(seq_length - 2) if self.__deps[idx] != Dep.NODEP])
        self.__stack = collections.deque([])
        if self.__buffer:
            self.__shift()
        self.arcs = []  # Tuples (dep, parent_idx, child_idx)

    def __pdep(self, child_idx):
        pdep = self.__deps[child_idx]
        if pdep == Dep.ROOT:
            return Dep.SPLIT  # ROOT cannot have any parent
        return pdep

    def __shift(self):
        self.__stack.append(self.__buffer.popleft())

    def __reduce(self):
        self.__stack.pop()
        if not self.__stack:
            self.__shift()

    @property
    def complete(self):
        return not self.__buffer

    @property
    def root(self):
        cands = set()
        cannot_be_root = set()
        for _, pdix, cidx in self.arcs:
            cands |= {pdix, cidx}
            cannot_be_root.add(cidx)
        try:
            return sorted(cands - cannot_be_root)[0]
        except IndexError:
            return None

    @property
    def mats(self):
        """Materials for predicting the next transition"""
        mask_1, mask_2 = make_masks(self.__stack[-1] + 1, self.__buffer[0] + 1)
        return self.__tag_codes, self.__dep_codes, self.__char_codes, self.__word_vectors, mask_1, mask_2

    def register_transition(self, trans):
        if trans == Trans.LEFT:
            self.arcs.append((self.__pdep(self.__stack[-1]), self.__buffer[0], self.__stack[-1]))
            self.__reduce()
        elif trans == Trans.RIGHT:
            self.arcs.append((self.__pdep(self.__buffer[0]), self.__stack[-1], self.__buffer[0]))
            self.__shift()
        elif trans == Trans.REDUCE:
            self.__reduce()
        elif trans == Trans.SHIFT:
            self.__shift()


def _build_tree(parse):
    """Converts parse to tree, returns None if no root is detected"""
    root = parse.root
    if root is None:
        return None
    else:
        tree = Tree(root)
        for dep, parent_idx, child_idx in parse.arcs:
            tree.register_child(dep, parent_idx, child_idx)
        return tree


class Parser(object):

    def __init__(self, language_model, batch_size):
        self.__batch_size = batch_size
        self.__charset = Charset().load()
        self.__wordset = Wordset(language_model).load()
        self.__ptags_model = PTagsModel(len(self.__charset)).load()
        self.__pdeps_model = PDepsModel(len(self.__charset)).load()
        self.__trans_model = TransModel(len(self.__charset)).load()

    def __call__(self, token_lists):
        """Parses sentences by batch"""
        mats = run_multithreads(token_lists, self.__vectorize_sentence, cfg.NB_PROCESSES)
        batches = make_batches(mats, self.__batch_size)
        all_parses = []
        for batch in batches:
            seq_lengths, char_codes, word_vectors = zip(*batch)
            tag_codes = self.__predict_tags(char_codes, word_vectors)
            dep_codes = self.__predict_deps(tag_codes, char_codes, word_vectors)
            for idx, seq_length in enumerate(seq_lengths):
                all_parses.append(
                    _Parse(seq_length, tag_codes[idx], dep_codes[idx], char_codes[idx], word_vectors[idx]))
        # Predict transitions
        incomplete_parses = [parse for parse in all_parses if not parse.complete]
        while incomplete_parses:
            parse_batches = make_batches(incomplete_parses, self.__batch_size)
            for batch in parse_batches:
                self.__predict_transitions(batch)
            incomplete_parses = [parse for parse in all_parses if not parse.complete]
        # Prepare results
        all_tags = [parse.tags for parse in all_parses]
        all_trees = run_multithreads(all_parses, _build_tree, cfg.NB_PROCESSES)
        return all_tags, all_trees

    def __vectorize_sentence(self, tokens):
        return vectorize_sentence(tokens, self.__charset, self.__wordset)

    def __predict_tags(self, char_codes, word_vectors):
        return self.__ptags_model.predict(char_codes, word_vectors)

    def __predict_deps(self, tag_codes, char_codes, word_vectors):
        return self.__pdeps_model.predict(tag_codes, char_codes, word_vectors)

    def __predict_transitions(self, parses):
        """Predicts next transitions & registers them in place"""
        tag_codes, dep_codes, char_codes, word_vectors, masks_1, masks_2 = zip(*[parse.mats for parse in parses])
        predictions = self.__trans_model.predict(tag_codes, dep_codes, char_codes, word_vectors, masks_1, masks_2)
        for idx, trans in enumerate(predictions):
            parses[idx].register_transition(trans)
