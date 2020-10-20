from scrappybara.utils.mutables import append_in_dict_dict_list


class Tree:
    """N-tree.
    Nodes have to be hashable & unique.
    """

    def __init__(self, root):
        self.root = root
        self.__children = {}  # Node => {label: list_nodes}
        self.__parents = {}  # Node => (label, node)

    def __iter__(self):
        self.__iter = iter(self.__parents.items())
        return self

    def __next__(self):
        """Arc iterator"""
        child, rparent = next(self.__iter)
        label, parent = rparent
        return label, parent, child

    def __len__(self):
        return 1 + len(self.__parents.keys())

    def register_child(self, label, parent, child):
        assert parent != child
        append_in_dict_dict_list(self.__children, parent, label, child)
        self.__parents[child] = (label, parent)

    @property
    def nodes(self):
        return [self.root] + list(self.__parents.keys())

    def has_node(self, node):
        return any([node in self.__children, node in self.__parents])

    def ancestors_via(self, node, label):
        """Starting from a node, tries to climb the tree as far as possible via a label.
        The furthest ancestor is the first element of the branch.
        The branch does not contain the argument node.
        """
        anc_branch = []

        def _recurse_climb(_child):
            _label_node = self.parent(_child)
            if _label_node is not None:
                _parent_label, _parent_node = _label_node
                if _parent_label == label:
                    anc_branch.append(_parent_node)
                    _recurse_climb(_parent_node)

        _recurse_climb(node)
        anc_branch.reverse()
        return anc_branch

    def descendants_via(self, node, label):
        """Flat list of nodes below an ancestor.
        For each child branch, tries to go down as far as possible via a label.
        """
        nodes = []

        def _recurse_add_descendants(_parent):
            try:
                _label_children = self.__children[_parent]
                for _child in _label_children[label]:
                    nodes.append(_child)
                    _recurse_add_descendants(_child)
            except KeyError:
                return

        _recurse_add_descendants(node)
        return nodes

    def parent(self, node):
        """Returns tuple (label, parent) or None if no parent"""
        try:
            return self.__parents[node]
        except KeyError:
            return None

    def has_parent_via(self, node, label):
        try:
            return self.__parents[node][0] == label
        except KeyError:
            return False

    def has_parent_via_set(self, node, labels):
        try:
            return self.__parents[node][0] in labels
        except KeyError:
            return False

    def children(self, node):
        """Returns list of tuples (label, child)"""
        try:
            return [(label, child) for label, children in self.__children[node].items() for child in children]
        except KeyError:
            return []

    def children_via(self, node, label):
        try:
            return self.__children[node][label]
        except KeyError:
            return []

    def child_via(self, node, label):
        """Returns first child found via a label"""
        try:
            return self.__children[node][label][0]
        except KeyError:
            return None

    def has_child_via(self, node, label):
        try:
            return label in self.__children[node]
        except KeyError:
            return False

    def has_child_via_set(self, node, labels):
        try:
            return any([key in labels for key in self.__children[node]])
        except KeyError:
            return False

    def siblings(self, node):
        try:
            _, parent = self.__parents[node]
            siblings = []
            for label, children in self.__children[parent].items():
                for child in children:
                    if child != node:
                        siblings.append((label, child))
            return siblings
        except KeyError:
            return []
