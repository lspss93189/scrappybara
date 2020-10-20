import collections

import numpy as np

from scrappybara.semantics.resources import Entity
from scrappybara.syntax.tags import Tag
from scrappybara.utils.files import load_pkl_file
from scrappybara.utils.maths import cosine


def extract_lexeme_bag(nodes):
    """Extracts a bag of lexemes from a list of nodes"""
    return collections.Counter([n.canon for n in nodes if n.is_lexeme])


class EntityLinker(object):

    def __init__(self):
        self.__str_ids = load_pkl_file('entities', 'str_ids.pkl')  # str => list of entity ids
        self.__id_vector = load_pkl_file('entities', 'id_vector.pkl')  # id => vector (dict of idx => count)
        lexemes = load_pkl_file('entities', 'lexemes.pkl')
        self.__lexeme_idx = {lexeme: idx for idx, lexeme in enumerate(lexemes)}  # lexeme => idx

    def __call__(self, nodes):
        """Links proper nouns to entity IDs.
        Creates Entity object and attaches it to the Node in place.
        Returns a consolidated list of tuple (propn, entity)"""
        to_disambiguate = []
        for node in [n for n in nodes if n.tag == Tag.PROPN]:
            try:
                entity_ids = self.__str_ids[node.canon]
                if len(entity_ids) > 1:
                    # Ambiguity
                    to_disambiguate.append((node, entity_ids))
                elif len(entity_ids) == 1:
                    node.resource = Entity(entity_ids[0])
            except (KeyError, IndexError):
                continue
        # Disambiguate
        if len(to_disambiguate):
            vector = self.__vectorize(nodes)
            for node, entity_ids in to_disambiguate:
                cosines = [cosine(vector, self.__id_vector[entity_id]) for entity_id in entity_ids]
                node.resource = Entity(entity_ids[np.argmax(cosines)])
        return [(node.original, node.resource) for node in nodes if node.resource is not None]

    def __vectorize(self, nodes):
        """Returns sparse vector of a text"""
        lexeme_counter = extract_lexeme_bag(nodes)
        vector = {}
        for lexeme, count in lexeme_counter.items():
            if lexeme in self.__lexeme_idx:
                vector[self.__lexeme_idx[lexeme]] = count
        return vector
