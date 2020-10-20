from scrappybara.syntax.dependencies import Dep, MARKER_DEPS
from scrappybara.syntax.tags import NOUN_TAGS
from scrappybara.utils.mutables import append_to_dict_list


def _chunk(noun, compound_nouns):
    """Recursively finds compound nouns by using dictionary"""
    nouns = [noun]

    def _chunk_recursive(_noun):
        for _cnoun in compound_nouns.get(_noun, []):
            nouns.append(_cnoun)
            _chunk_recursive(_cnoun)

    _chunk_recursive(noun)
    nouns.sort(key=lambda x: x.idx)
    return ' '.join([n.lemma for n in nouns])


class Chunker(object):

    def __call__(self, nodes, node_tree):
        """Detects chunk of common nouns via complements"""
        compound_nouns = {}  # node => list of compound nouns
        have_parent = set()
        for noun in [n for n in nodes if n.tag in NOUN_TAGS]:
            dep_parent = node_tree.parent(noun)
            if dep_parent is not None:
                dep, parent = dep_parent
                if dep == Dep.CPL and not node_tree.has_child_via_set(noun, MARKER_DEPS) and noun.idx < parent.idx \
                        and parent.tag in NOUN_TAGS:
                    append_to_dict_list(compound_nouns, parent, noun)
                    have_parent.add(noun)
        for root in [n for n in nodes if n in compound_nouns and n not in have_parent]:
            root.chunk = _chunk(root, compound_nouns)
