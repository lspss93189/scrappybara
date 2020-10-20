"""Interface for labelled sentences.
A token tuple has 4 elements: (token, tag name, dependency name, parent 0-idx).
The parent idx is equal to -1 when the token has no parent (NODEP or ROOT).
e.g. if we have 2 sentences:
  "I eat apples.", "You drink soda."
The labelled data is a list of list of token tuples:
  [[('I', 'PRON', 'SUBJ', 1), ('eat', 'VERB', 'ROOT', -1), ('apples', 'NOUN', 'OBJ', 1), ('.', 'PUNCT', 'NODEP', -1)],
   [('You', 'PRON', 'SUBJ', 1), ('drink', 'VERB', 'ROOT', -1), ('soda', 'NOUN', 'OBJ', 1), ('.', 'PUNCT', 'NODEP', -1)]]
"""

import collections
import json
import random

from scrappybara.syntax.dependencies import Dep
from scrappybara.syntax.tags import Tag
from scrappybara.syntax.training_samples import PDepsSample, PTagsSample, TransSample
from scrappybara.syntax.transitions import Trans
from scrappybara.utils.mutables import append_to_dict_list
from scrappybara.utils.tree import Tree


def _arcs_are_crossing(arc_1, arc_2):
    arc_1, arc_2 = sorted([sorted(arc_1), sorted(arc_2)])
    return arc_1[0] < arc_2[0] < arc_1[1] < arc_2[1]


def extract_ptags_training_data(token_tuple_lists, charset, wordset):
    # Extract & shuffle samples
    labelled_sents = [LabelledSentence(idx, tuple_list) for idx, tuple_list in enumerate(token_tuple_lists)]
    ptags_samples = [PTagsSample(sent.tokens, sent.tags, charset, wordset) for sent in labelled_sents]
    random.shuffle(ptags_samples)
    # Prepare tensors
    data_per_sample = [ptags_sample.training_mats for ptags_sample in ptags_samples]
    return [list(data) for data in zip(*data_per_sample)]


def extract_pdeps_training_data(token_tuple_lists, charset, wordset):
    # Extract & shuffle samples
    labelled_sents = [LabelledSentence(idx, tuple_list) for idx, tuple_list in enumerate(token_tuple_lists)]
    pdeps_samples = [PDepsSample(sent.tokens, sent.tags, sent.deps, charset, wordset) for sent in labelled_sents]
    random.shuffle(pdeps_samples)
    # Prepare tensors
    data_per_sample = [pdeps_sample.training_mats for pdeps_sample in pdeps_samples]
    return [list(data) for data in zip(*data_per_sample)]


def extract_trans_training_data(token_tuple_lists, charset, wordset):
    # Extract & shuffle samples
    labelled_sents = [LabelledSentence(idx, tuple_list) for idx, tuple_list in enumerate(token_tuple_lists)]
    trans_samples = []
    for idx, sent in enumerate(labelled_sents):
        for idx_1, idx_2, transition in sent.transitions:
            trans_samples.append(
                TransSample(sent.tokens, sent.tags, sent.deps, idx_1, idx_2, transition, charset, wordset))
    random.shuffle(trans_samples)
    # Prepare tensors
    data_per_sample = [trans_sample.training_mats for trans_sample in trans_samples]
    return [list(data) for data in zip(*data_per_sample)]


class LabelledSentence(object):
    """Sentence parsed by a human"""

    def __init__(self, sentence_id, token_tuples):
        self.id = sentence_id
        self.__warnings = {}  # Token idx => warning message (jsonnable dictionary)
        self.tokens = []  # Original tokens (case sensitive)
        self.tags = []  # Part-of-speech tag for each token (enums)
        self.deps = []  # Dependency to parent for each token (enums)
        self.tree = None  # Does not contain NODEP tokens
        # Read parse
        root_idx = None
        for child_idx, token_tag_dep_pidx in enumerate(token_tuples):
            if Dep[token_tag_dep_pidx[2]] == Dep.ROOT:
                root_idx = child_idx
                break
        if root_idx is not None:
            self.tree = Tree(root_idx)
            for child_idx, token_tag_dep_pidx in enumerate(token_tuples):
                token, tag, dep, parent_idx = token_tag_dep_pidx
                dep = Dep[dep]
                self.tokens.append(token)
                self.tags.append(Tag[tag])
                self.deps.append(dep)
                if dep not in {Dep.ROOT, Dep.NODEP} and parent_idx > -1:
                    self.tree.register_child(dep, parent_idx, child_idx)

    def __str__(self):
        return ' '.join(self.tokens)

    def __repr__(self):
        return ' '.join(self.tokens)

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, item):
        return self.tokens[item]

    def __iter__(self):
        return iter(self.tokens)

    def _is_parent(self, parent_idx, child_idx):
        dep_idx = self.tree.parent(child_idx)
        if dep_idx is not None:
            _, idx = dep_idx
            return idx == parent_idx
        return False

    def _has_arc_before(self, token_idx, max_idx):
        """Token has parent or child before max_idx"""
        # Check parent
        dep_idx = self.tree.parent(token_idx)
        if dep_idx is not None:
            _, parent_idx = dep_idx
            if parent_idx < max_idx:
                return True
        # Check children
        for _, child_idx in self.tree.children(token_idx):
            if child_idx < max_idx:
                return True
        return False

    def register_warning(self, token_idx, comment, focus_idxs):
        warning = {'comment': comment, 'focusIdxs': focus_idxs}
        append_to_dict_list(self.__warnings, token_idx, warning)

    @property
    def warnings_json(self):
        """Returns a JSON string if parsing warnings have been flagged, None otherwise"""
        if self.__warnings:
            return json.dumps(self.__warnings, ensure_ascii=False)
        return None

    @property
    def valid_idxs(self):
        """Indexes of tokens that are not NODEP"""
        result = []
        for idx, token in enumerate(self.tokens):
            if self.deps[idx] != Dep.NODEP:
                result.append(idx)
        return result

    def is_leaf(self, idx):
        return not bool(self.tree.children(idx))

    def have_crossing_arcs(self, child_idx_1, child_idx_2):
        """Check if arcs are crossing given 2 child-node indexes"""
        if any([child_idx_1 == self.tree.root, child_idx_2 == self.tree.root]):
            return False

        def _arc(_idx):
            return self.tree.parent(_idx)[1], _idx

        return _arcs_are_crossing(_arc(child_idx_1), _arc(child_idx_2))

    @property
    def transitions(self):
        """Deducts the list of transitions from parse"""
        stack = collections.deque([])
        buffer = collections.deque(self.valid_idxs)

        def _reduce():
            stack.pop()

        def _shift():
            stack.append(buffer.popleft())

        if buffer:
            _shift()

        transitions = []  # List of tuples (idx_1, idx_2, transition)
        while buffer:
            if not stack:
                _shift()
            elif self._is_parent(buffer[0], stack[-1]):
                transitions.append((stack[-1], buffer[0], Trans.LEFT))
                _reduce()
            elif self._is_parent(stack[-1], buffer[0]):
                transitions.append((stack[-1], buffer[0], Trans.RIGHT))
                _shift()
            elif self._has_arc_before(buffer[0], stack[-1]):
                transitions.append((stack[-1], buffer[0], Trans.REDUCE))
                _reduce()
            else:
                transitions.append((stack[-1], buffer[0], Trans.SHIFT))
                _shift()
        return transitions
