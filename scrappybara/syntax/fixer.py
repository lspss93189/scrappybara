from scrappybara.syntax.dependencies import Dep, PROP_DEPS
from scrappybara.syntax.tags import Tag, NOUN_TAGS


class Fixer(object):

    def __init__(self, adjs, nouns):
        self.__adjs = adjs
        self.__nouns = nouns

    def __call__(self, node, node_tree):
        """Fixes predictions from oracles"""
        if not node_tree.children(node):
            dep_parent = node_tree.parent(node)
            if dep_parent:
                dep, parent = dep_parent
                if any([dep == Dep.CPL and parent.tag in NOUN_TAGS, dep in PROP_DEPS]):
                    if node.lemma in self.__adjs and node.tag in NOUN_TAGS:
                        node.tag = Tag.ADJ
                    elif node.lemma in self.__nouns and node.tag == Tag.ADJ:
                        node.tag = Tag.NOUN
