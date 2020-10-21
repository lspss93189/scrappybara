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

    def __init__(self):
        self.__str_ids = load_pkl_file('entities', 'str_ids.pkl')  # str => list of entity ids
        self.__id_vector = load_pkl_file('entities', 'id_vector.pkl')  # id => vector (dict of idx => count)
        lexemes = load_pkl_file('entities', 'lexemes.pkl')
        self.__lexeme_idx = {lexeme: idx for idx, lexeme in enumerate(lexemes)}  # lexeme => idx

    def __call__(self, nodes, original_text):
        """Links proper nouns to entity IDs.
        Creates Entity object and attaches it to the Node in place.
        Returns a consolidated list of tuple (propn, entity)"""
        to_disambiguate = []
        nodes_eids = []  # list of tuples (node, entity_id)
        for node in [n for n in nodes if n.tag == Tag.PROPN]:
            try:
                entity_ids = self.__str_ids[node.canon]
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
                cosines = [cosine(vector, self.__id_vector[entity_id]) for entity_id in entity_ids]
                nodes_eids.append((node, entity_ids[np.argmax(cosines)]))
        # Find boundaries
        unique_forms = {node.original for node, _ in nodes_eids}
        form_boundaries = {form: _find_boundaries(form, original_text) for form in unique_forms}
        for node, entity_id in sorted(nodes_eids, key=lambda x: x[0].idx):
            try:
                boundaries = next(form_boundaries[node.original])
            except StopIteration:
                boundaries = (None, None)
            node.resource = Entity(entity_id, node.original, *boundaries)
        return [node.resource for node in nodes if type(node.resource) == Entity]

    def __vectorize(self, nodes):
        """Returns sparse vector of a text"""
        lexeme_counter = extract_lexeme_bag(nodes)
        vector = {}
        for lexeme, count in lexeme_counter.items():
            if lexeme in self.__lexeme_idx:
                vector[self.__lexeme_idx[lexeme]] = count
        return vector
