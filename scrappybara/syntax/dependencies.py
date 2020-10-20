import enum


@enum.unique
class Dep(enum.IntEnum):
    """Syntactic label from a child word to its parent"""

    # OUT OF TREE
    # -------------------------------------------------------------------------->

    PAD = 0  # Batch padding (0's)
    NODEP = 1  # e.g. punctuation

    # ROOT
    # -------------------------------------------------------------------------->

    ROOT = 2

    # IN TREE
    # -------------------------------------------------------------------------->

    AND = 3
    ART = 4
    AUX = 5
    CALLEE = 6
    CMARK = 7
    CPL = 8
    EXIST = 9
    FLAT = 10
    IMARK = 11
    INTJ = 12
    IOBJ = 13
    IPROP = 14
    MARK = 15
    MODAL = 16
    NEG = 17
    OBJ = 18
    OR = 19
    ORPHAN = 20
    PART = 21
    PROP = 22
    SPLIT = 23
    SUBJ = 24


NB_DEPS = len([dep for dep in Dep])

# Sets
MARKER_DEPS = {Dep.MARK, Dep.CMARK, Dep.IMARK}
PROP_DEPS = {Dep.PROP, Dep.IPROP}
CCONJ_DEPS = {Dep.AND, Dep.OR}

# Verb descendants
VERB_ARG_DEPS = {Dep.EXIST, Dep.SUBJ, Dep.OBJ, Dep.IOBJ, Dep.PROP, Dep.IPROP}
VERB_ARG_2_PLUS_DEPS = VERB_ARG_DEPS - {Dep.SUBJ}
VERB_CHILD_DEPS = VERB_ARG_DEPS | {Dep.AUX, Dep.MODAL}

# Dependents that carry no semantics
FUNCTIONAL_DEPS = {Dep.ART, Dep.AUX, Dep.CMARK, Dep.NEG, Dep.INTJ, Dep.MARK, Dep.IMARK, Dep.PART, Dep.MODAL}
