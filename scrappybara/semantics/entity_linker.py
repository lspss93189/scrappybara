import scrappybara.config as cfg
import numpy as np
from scrappybara.syntax.dependencies import Dep, MARKER_DEPS
from scrappybara.syntax.tags import Tag
from scrappybara.utils.files import load_pkl_file
from scrappybara.utils.maths import cosine
from scrappybara.utils.mutables import append_to_dict_list
from scrappybara.semantics.entity import Entity


class EntityLinker(object):
    __noun_tags = {Tag.NOUN, Tag.PROPN}
    __linking_threshold = 0.0  # Minimum cosine required to link an entity

    def __init__(self):
        self.__form_eids = load_pkl_file(cfg.DATA_DIR / 'entities' / 'form_eids.pkl')  # form => list of entity ids
        self.__eid_vector = load_pkl_file(cfg.DATA_DIR / 'entities' / 'eid_vector.pkl')  # eID => dict sparce vector

    def __call__(self, node_dict, node_tree, doc_vector, original_text):
        """Returns entities found in a single sentence"""
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
            entity = self.__chunk(root, noun_parts, node_tree, doc_vector, original_text)
            if entity is not None:
                entities.append(entity)
        return entities

    def __link_form_to_entity(self, form, eids, vector, text):
        """Tries to link a form to an entity.
        Returns None if not possible.
        """
        scores = [cosine(vector, self.__eid_vector[eid]) for eid in eids]
        if max(scores) > self.__linking_threshold:
            selected_eid = eids[np.argmax(scores)]
            return Entity(selected_eid, form, 0, 0)
        return None

    def __chunk(self, root, noun_parts, node_tree, vector, text):
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
        for i in range(len(parts) - 1):
            form = ' '.join([node.standard for node in parts[i:]])
            eids = self.__form_eids[form]
            entity = self.__link_form_to_entity(form, eids, vector, text)
            if entity is not None:
                root.entity = entity
                return entity
        return None
