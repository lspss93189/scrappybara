import collections
import re
import numpy as np

from scrappybara.semantics.resources import Entity
from scrappybara.syntax.tags import Tag
from scrappybara.utils.files import load_pkl_file
from scrappybara.utils.maths import cosine


def extract_lexeme_bag(nodes):
    """Extracts a bag of lexemes from a list of nodes"""
    return collections.Counter([n.canon for n in nodes if n.is_lexeme])


def _find_boundaries(form, text):
    return iter([match.span() for match in re.finditer(form, text)])


class EntityLinker(object):

    def __init__(self, form_eids):
        self.__form_eids = form_eids
        self.__eid_vector = load_pkl_file('entities', 'id_vector.pkl')  # entity id => vector (dict of idx => count)
        self.__lexeme_idx_idf = load_pkl_file('entities', 'lexemes.pkl')  # lexeme => (idx, idf score)

    def __call__(self, nodes, original_text):
        """Links proper nouns to entity IDs.
        Creates Entity object and attaches it to the Node in place.
        Returns a consolidated list of tuple (propn, entity)"""
        to_disambiguate = []
        nodes_eids = []  # list of tuples (node, entity_id)
        for node in [n for n in nodes if n.tag == Tag.PROPN]:
            try:
                entity_ids = self.__form_eids[node.canon]
                if len(entity_ids) > 1:
                    # Ambiguity
                    to_disambiguate.append((node, entity_ids))
                elif len(entity_ids) == 1:
                    # No ambiguity
                    nodes_eids.append((node, entity_ids[0]))
            except (KeyError, IndexError):
                continue
        # Disambiguate
        if len(to_disambiguate):
            vector = self.__vectorize(nodes)
            for node, entity_ids in to_disambiguate:
                scores = [cosine(vector, self.__eid_vector[entity_id]) for entity_id in entity_ids]
                nodes_eids.append((node, entity_ids[np.argmax(scores)]))
        # Find boundaries
        unique_forms = {node.text for node, _ in nodes_eids}
        form_boundaries = {form: _find_boundaries(form, original_text) for form in unique_forms}
        for node, entity_id in sorted(nodes_eids, key=lambda x: x[0].idx):
            try:
                boundaries = next(form_boundaries[node.text])
            except StopIteration:
                boundaries = (None, None)
            node.resource = Entity(entity_id, node.text, *boundaries)
        return [node.resource for node in nodes if type(node.resource) == Entity]

    def __vectorize(self, nodes):
        """Returns sparse vector of a text"""
        lexeme_counter = extract_lexeme_bag(nodes)
        total_count = sum(lexeme_counter.values())
        vector = {}
        for lexeme, count in lexeme_counter.items():
            if lexeme in self.__lexeme_idx_idf:
                idx, idf = self.__lexeme_idx_idf[lexeme]
                vector[idx] = (count / total_count) * idf
        return vector
