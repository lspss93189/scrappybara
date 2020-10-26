from scrappybara.normalization.canonicalizer import Canonicalizer
from scrappybara.normalization.lemmatizer import Lemmatizer
from scrappybara.syntax.chunker import Chunker
from scrappybara.syntax.fixer import Fixer
from scrappybara.syntax.labelled_data import LabelledSentence
from scrappybara.syntax.nodifier import Nodifier
from scrappybara.utils.files import load_dict_from_txt_file, load_set_from_txt_file
from scrappybara.utils.mutables import reverse_dict


class LabelledSentencePipeline(object):
    """Contains all steps to process a sentence that is already labelled"""

    def __init__(self, language_model, form_eids):
        # Irregular lemmatization/inflection
        preterits = load_dict_from_txt_file('data/english', 'irregular_preterits.txt')
        pps = load_dict_from_txt_file('data/english', 'irregular_past_participles.txt')
        plurals = load_dict_from_txt_file('data/english', 'irregular_plurals.txt')
        comps = load_dict_from_txt_file('data/english', 'irregular_comparatives.txt')
        sups = load_dict_from_txt_file('data/english', 'irregular_superlatives.txt')
        nouns = load_set_from_txt_file('data/english', 'nouns.txt')
        adjs = load_set_from_txt_file('data/english', 'adjectives.txt')
        reversed_pps = reverse_dict(pps)  # lemma => past participle
        # Pipeline steps
        self.__nodify = Nodifier()
        self.__chunk = Chunker(form_eids)
        self.__lemmatize = Lemmatizer(language_model, adjs, preterits, pps, plurals, comps, sups, reversed_pps)
        self.__fix = Fixer(adjs, nouns)
        self.__canonicalize = Canonicalizer(self.__lemmatize)

    def _process_sentence(self, sentence_pack):
        """Args are packed into a list of args so this process can be multithreaded"""
        tokens, tags, idx_tree = sentence_pack
        # Nofification
        node_dict, node_tree = self.__nodify(tokens, tags, idx_tree)
        # Chunking
        node_dict = self.__chunk(node_dict, node_tree)  # removes nodes consumed by chunks
        node_without_chunk = [n for n in node_dict.values() if n.chunk is None]
        # Lemmatization
        for node in node_without_chunk:
            node.lemma, node.suffix = self.__lemmatize(node.standard, node.tag)
        # Fixing
        for node in node_without_chunk:
            self.__fix(node, node_tree)
        # Canonicalization
        for node in node_dict.values():
            self.__canonicalize(node)
        return node_dict

    # TESTING
    # -------------------------------------------------------------------------->

    def process_labelled_sentence(self, token_tuples):
        sent = LabelledSentence(0, token_tuples)
        _, stuples = self._process_sentence([sent.tokens, sent.tags, sent.tree])
        return stuples
