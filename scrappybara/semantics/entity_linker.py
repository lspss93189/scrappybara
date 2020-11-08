import math

import numpy as np

from scrappybara.semantics.entity import Entity
from scrappybara.syntax.dependencies import Dep, MARKER_DEPS
from scrappybara.syntax.tags import Tag
from scrappybara.utils.maths import cosine
from scrappybara.utils.mutables import append_to_dict_list


class EntityLinker(object):
    __noun_tags = {Tag.NOUN, Tag.PROPN}
    __linking_threshold = 0.1  # Minimum cosine required to link an entity

    def __init__(self, form_eids, feature_dc, eid_bag, total_docs):
        self.__form_eids = form_eids
        self.__feature_idx = {feature_dc[0]: idx for idx, feature_dc in enumerate(feature_dc)}
        self.__idx_dc = {idx: feature_dc[1] for idx, feature_dc in enumerate(feature_dc)}
        self.__eid_bag = eid_bag
        self.__total_docs = total_docs
        self.__eid_vector = {}  # Cache of vectors

    def __call__(self, node_dict, node_tree, vector):
        """Returns list of entities found in a single sentence"""
        noun_parts = {node: [] for node in node_dict.values() if node.tag in self.__noun_tags}  # node => list of parts
        have_parent_noun = set()
        for part in noun_parts.keys():
            dep_parent = node_tree.parent(part)
            if dep_parent is not None:
                dep, parent = dep_parent
                if all([dep == Dep.CPL, not node_tree.has_child_via_set(part, MARKER_DEPS), part.idx < parent.idx,
                        parent.tag in self.__noun_tags]):
                    append_to_dict_list(noun_parts, parent, part)
                    have_parent_noun.add(part)
        # Register entities
        entities = []
        for root in [n for n in noun_parts if n not in have_parent_noun]:
            entity = self.__chunk(root, noun_parts, node_tree, vector)
            if entity is not None:
                entities.append(entity)
        return entities

    def __link_form_to_entity(self, form, eids, vector):
        """Tries to link a form to an entity.
        Returns None if not possible.
        """
        # Vectorize all candidates
        cand_vectors = []
        for eid in eids:
            try:
                cand_vectors.append(self.__eid_vector[eid])
            except KeyError:
                vector = self.__vectorize(self.__eid_bag[eid])
                cand_vectors.append(vector)
                self.__eid_vector[eid] = vector
        # Disambiguate
        scores = [cosine(vector, cand_vector) for cand_vector in cand_vectors]
        if max(scores) > self.__linking_threshold:
            selected_eid = eids[np.argmax(scores)]
            return Entity(selected_eid, form)
        return None

    def __chunk(self, root, noun_parts, node_tree, vector):
        """Recursively builds a noun-phrase & converts it to an Entity if possible"""
        parts = [root]

        def _naked_adjs(_noun):
            _adjs = []
            for _cpl in node_tree.children_via(_noun, Dep.CPL):
                if _cpl.tag == Tag.ADJ and not node_tree.has_child_via_set(_cpl, MARKER_DEPS):
                    _adjs.append(_cpl)
            return _adjs

        def _chunk_recursive(_noun):
            parts.extend(_naked_adjs(_noun))
            for _part in noun_parts.get(_noun, []):
                parts.append(_part)
                _chunk_recursive(_part)

        _chunk_recursive(root)
        parts.sort(key=lambda x: x.idx)
        for i in range(len(parts)):
            form = ' '.join([node.standard for node in parts[i:]])
            if form in self.__form_eids:
                eids = list(self.__form_eids[form])
                entity = self.__link_form_to_entity(form, eids, vector)
                if entity is not None:
                    root.entity = entity
                    return entity
        return None

    def __vectorize(self, idx_count):
        """Returns sparse vector, given a bag of features"""
        total_count = sum([count for _, count in idx_count])
        vector = {}  # idx of feature => score tf.idf
        for idx, count in idx_count:
            dc = self.__idx_dc[idx]
            vector[idx] = (count / total_count) * math.log(self.__total_docs / dc)
        return vector

    def vectorize(self, bag_feature_count):
        """Production method: converts features into idxs"""
        bag_idx_count = [(self.__feature_idx[feature], count) for feature, count in bag_feature_count if
                         feature in self.__feature_idx]
        return self.__vectorize(bag_idx_count)
