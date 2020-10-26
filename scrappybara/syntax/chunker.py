from scrappybara.syntax.dependencies import Dep, MARKER_DEPS
from scrappybara.syntax.tags import PROP_TAGS, NOUN_TAGS
from scrappybara.utils.mutables import append_to_dict_list


def _chunk(root, noun_parts, form_eids):
    """Recursively finds parts of a noun-phrase.
    Returns set of nodes that are parts of a noun-phrase.
    """
    parts = [root]

    def _chunk_recursive(_noun):
        for _part in noun_parts.get(_noun, []):
            parts.append(_part)
            _chunk_recursive(_part)

    _chunk_recursive(root)
    parts.sort(key=lambda x: x.idx)
    for i in range(len(parts) - 1):
        cand = ' '.join([node.standard for node in parts[i:]])
        if cand in form_eids:
            root.chunk = cand
            return set(parts[i:-1])
    return set()


class Chunker(object):

    def __init__(self, form_eids):
        self.__form_eids = form_eids  # form => list of entity ids

    def __call__(self, node_dict, node_tree):
        """Detects parts of noun-phrases via CPL"""
        noun_parts = {}  # node => list of parts
        have_parent = set()
        for part in [n for n in node_dict.values() if n.tag in PROP_TAGS]:
            dep_parent = node_tree.parent(part)
            if dep_parent is not None:
                dep, parent = dep_parent
                if all([dep == Dep.CPL, not node_tree.has_child_via_set(part, MARKER_DEPS), part.idx < parent.idx,
                        parent.tag in NOUN_TAGS]):
                    append_to_dict_list(noun_parts, parent, part)
                    have_parent.add(part)
        # Register chunks
        flattened = set()
        for root in [n for n in node_dict.values() if n in noun_parts and n not in have_parent]:
            flattened |= _chunk(root, noun_parts, self.__form_eids)
        # Clean nodes
        return {idx: node for idx, node in node_dict.items() if node not in flattened}
