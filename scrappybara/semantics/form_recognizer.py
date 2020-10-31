import scrappybara.config as cfg
from scrappybara.syntax.dependencies import Dep, MARKER_DEPS
from scrappybara.syntax.tags import Tag
from scrappybara.utils.files import load_pkl_file
from scrappybara.utils.mutables import append_to_dict_list


def _chunk(root, noun_parts, node_tree, form_eids):
    """Recursively finds parts of a noun-phrase.
    Returns set of nodes that are parts of a noun-phrase.
    """
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
        cand = ' '.join([node.standard for node in parts[i:]])
        if cand in form_eids:
            root.form = cand
            root.eids = form_eids[cand]
            return


class FormRecognizer(object):
    __noun_tags = {Tag.NOUN, Tag.PROPN}

    def __init__(self):
        self.__form_eids = load_pkl_file(cfg.DATA_DIR / 'entities' / 'form_eids.pkl')  # form => list of entity ids

    def __call__(self, nodes, node_tree):
        """Assign nodes' form & entity IDs, in place"""
        noun_parts = {node: [] for node in nodes if node.tag in self.__noun_tags}  # node => list of parts
        have_parent_noun = set()
        for part in noun_parts.keys():
            dep_parent = node_tree.parent(part)
            if dep_parent is not None:
                dep, parent = dep_parent
                if all([dep == Dep.CPL, not node_tree.has_child_via_set(part, MARKER_DEPS), part.idx < parent.idx,
                        parent.tag in self.__noun_tags]):
                    append_to_dict_list(noun_parts, parent, part)
                    have_parent_noun.add(part)
        # Register chunks
        for root in [n for n in noun_parts if n not in have_parent_noun]:
            _chunk(root, noun_parts, node_tree, self.__form_eids)
