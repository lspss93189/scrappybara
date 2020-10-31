from scrappybara.normalization.suffixes import Suffix
from scrappybara.syntax.tags import Tag


def _particle_compound(lemma, verb):
    if verb.particles:
        return ' '.join([lemma] + verb.particles)
    return lemma


class Canonicalizer(object):
    """The canonical version of a word is not always the lemma"""

    __personal_pronouns_object_to_subject = {
        'me': 'i',
        'you': 'you',
        'her': 'she',
        'him': 'he',
        'us': 'we',
        'them': 'they',
    }

    def __init__(self, lemmatizer):
        self.__lemmatize = lemmatizer

    def __call__(self, node):
        """Registers canonical representation of a node in place"""
        if node.form:
            node.canon = node.form
            return
        if node.tag == Tag.PRON and node.lemma in self.__personal_pronouns_object_to_subject:
            node.canon = self.__personal_pronouns_object_to_subject[node.lemma]
            return
        if node.tag == Tag.ADJ:
            lemma, suffix = self.__lemmatize(node.standard, Tag.VERB)
            if suffix == Suffix.PAST:
                node.suffix = suffix
                node.active_verb = _particle_compound(lemma, node)
            node.canon = _particle_compound(node.lemma, node)
            return
        if node.tag == Tag.VERB:
            node.canon = _particle_compound(node.lemma, node)
            return
        node.canon = node.lemma
