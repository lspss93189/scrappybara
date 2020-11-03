"""The nodification process happens right after parsing.
It creates a new tree with syntactic node objects by flattening words such as proper nouns & verbs with particles.
"""
from scrappybara.syntax.dependencies import Dep, FUNCTIONAL_DEPS
from scrappybara.syntax.node import Node
from scrappybara.syntax.tags import NOUN_TAGS
from scrappybara.utils.tree import Tree


def _link_determiner(det, node_tree):
    mark = node_tree.child_via(det, Dep.MARK)
    if mark and mark.standard == 'of':
        return ' '.join([det.standard, 'of'])
    return det.standard


class Nodifier(object):

    def __call__(self, tokens, standards, tags, idx_tree):
        # EDGE CASES
        # No node
        if idx_tree is None:
            return {}, None
        # Only root
        if len(idx_tree) == 1:
            root_node = Node(idx_tree.root, tokens[idx_tree.root], standards[idx_tree.root], tags[idx_tree.root])
            return {idx_tree.root: root_node}, Tree(root_node)
        # STANDARD CASES
        node_dict = {}  # first_idx => (dep, node)
        bl_idxs = set()  # Black list of token indexes (flat, particles, NODEP)
        # Detect NODEPs
        for idx, _ in enumerate(tokens):
            if not idx_tree.has_node(idx):
                bl_idxs.add(idx)
        # Flatten tokens
        for idx, token in enumerate(tokens):
            if not idx_tree.children(idx):
                dep_idx = idx_tree.parent(idx)
                if dep_idx is not None:
                    dep, parent_idx = dep_idx
                    if dep == Dep.FLAT:
                        anc_branch = idx_tree.ancestors_via(idx, Dep.FLAT)
                        anc_idx = anc_branch[0]
                        bl_idxs |= set([idx] + anc_branch)
                        flat = ' '.join([tokens[i] for i in anc_branch] + [token])
                        node_dict[anc_idx] = Node(idx, flat, flat.lower(), tags[idx])
        # Make verb/adj with particles
        for idx, token in enumerate(tokens):
            particle_idxs = []
            for child_dep, child_idx in idx_tree.children(idx):
                if child_dep == Dep.PART:
                    particle_idxs.append(child_idx)
            if particle_idxs:
                bl_idxs |= set(particle_idxs)
                node = Node(idx, token, standards[idx], tags[idx])
                for i in sorted(particle_idxs):
                    if i > idx:
                        node.particles.append(tokens[i].lower())
                    elif tokens[i].lower() == 'to':
                        node.is_inf_to = True
                node_dict[idx] = node
        # Make remaining nodes
        for idx, token in enumerate(tokens):
            if idx not in node_dict and idx not in bl_idxs:
                node_dict[idx] = Node(idx, token, standards[idx], tags[idx])
        # Make new parse tree
        node_tree = Tree(node_dict[idx_tree.root])
        for idx, node in node_dict.items():
            for child_dep, child_idx in idx_tree.children(idx):
                if child_idx in node_dict:
                    node_tree.register_child(child_dep, node, node_dict[child_idx])
        # Register determiners
        for node in [n for n in node_tree.nodes if n.tag in NOUN_TAGS]:
            arts = node_tree.descendants_via(node, Dep.ART)
            if arts:
                arts.sort(key=lambda x: x.idx)
                det_strs = []
                for art in [a for a in arts if a.standard != 'such']:
                    det_strs.append(_link_determiner(art, node_tree))
                node.det = ' '.join(det_strs)
        # Delete functional nodes (only keep nodes that carry meaning)
        node_dict = {node.idx: node for node in node_dict.values() if
                     not node_tree.has_parent_via_set(node, FUNCTIONAL_DEPS)}
        return node_dict, node_tree
