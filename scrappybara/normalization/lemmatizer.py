from scrappybara.normalization.suffixes import Suffix
from scrappybara.syntax.tags import Tag, NOUN_TAGS
from scrappybara.utils.text import ends_with_consonant, token_start, token_prefix, vowel_double_consonant_endings


class Lemmatizer(object):
    """Lemma's orthography is ruled by the language model"""

    # The lemmatizer will try to detect common prefixes
    __prefixes = {
        # Mostly for verbs
        're', 'un', 'mis', 'dis', 'out', 'co',
        # Mostly for nouns
        'sub', 'grand',
    }

    # Do not lemmatize
    __bare_ed = {'need'}
    __bare_men = {'acumen'}

    def __init__(self, language_model, adjs, preterit_lemma, pp_lemma, plural_lemma, comparative_lemma,
                 superlative_lemma, lemma_pp):
        self.__lm = language_model
        self.__adjs = adjs
        self.__preterit_lemma = preterit_lemma
        self.__pp_lemma = pp_lemma
        self.__plural_lemma = plural_lemma
        self.__comparative_lemma = comparative_lemma
        self.__superlative_lemma = superlative_lemma
        self.__lemma_pp = lemma_pp

    def __call__(self, standard, tag):
        """Returns lemma & suffix (suffix can be None)"""

        # FULL MATCH
        # -------------------------------------------------------------------------->

        if tag == Tag.VERB:
            if standard in {"'m", 'am', "'re", 'are'}:
                return 'be', None
            if standard in {"'s", 'is'}:
                return 'be', Suffix.THIRD_PERSON
            if standard == 'being':
                return 'be', Suffix.PROGRESSIVE
            if standard == 'has':
                return 'have', Suffix.THIRD_PERSON
            if standard == 'doing':
                return 'do', Suffix.PROGRESSIVE
            if standard in self.__bare_ed:
                return standard, None
        if tag == Tag.ADJ:
            if standard == 'better':
                return 'good', Suffix.COMPARATIVE
            if standard == 'best':
                return 'good', Suffix.SUPERLATIVE
        if tag == Tag.ADV:
            if standard == 'better':
                return 'well', Suffix.COMPARATIVE
            if standard == 'best':
                return 'well', Suffix.SUPERLATIVE
            if standard == "'":
                return "'s", None
        if tag in NOUN_TAGS:
            if standard == "'s":
                return 'we', None
            if standard in self.__bare_men:
                return standard, None

        # CONSULT FILES
        # -------------------------------------------------------------------------->

        lemma_suffix = self.__irregular_lemma(standard, tag)
        if lemma_suffix is not None:
            return lemma_suffix
        prefix_base = token_prefix(standard, self.__prefixes)
        if prefix_base is not None:
            prefix, base = prefix_base
            lemma_suffix = self.__irregular_lemma(base, tag)
            if lemma_suffix is not None:
                return prefix + lemma_suffix[0], lemma_suffix[1]

        # CONSULT LANGUAGE MODEL
        # -------------------------------------------------------------------------->

        def _lm_lemma(_start, _endings, _suffix):
            """Returns the best lemma according to the language model"""
            _best = self.__best_candidate(_start, _endings, tag)
            if _best is not None:
                return _best, _suffix
            # Try without the prefix: e.g. "[re-]forged", "[re]forged", "[grand]children"
            _prefix_base = token_prefix(_start, self.__prefixes)
            if _prefix_base is not None:
                _prefix, _base = _prefix_base
                _best = self.__best_candidate(_base, _endings, tag)
                if _best is not None:
                    return _prefix + _best, _suffix
            return standard, None

        # Adjectives
        # -------------------------------------------------------------------------->

        if tag == Tag.ADJ:
            # Min length 7: [fatt]est->fat, [tall]est->tall
            start = token_start(standard, 'est', 4)
            if start is not None:
                endings = vowel_double_consonant_endings(start)
                if endings is not None:
                    return _lm_lemma(start[:-2], endings, Suffix.SUPERLATIVE)
            # Min length 6: [fatt]er->fat, [tall]er->tall
            start = token_start(standard, 'er', 4)
            if start is not None:
                endings = vowel_double_consonant_endings(start)
                if endings is not None:
                    return _lm_lemma(start[:-2], endings, Suffix.COMPARATIVE)
            # Min length 6: [happ]iest->happy
            start = token_start(standard, 'iest', 2)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['y'], Suffix.SUPERLATIVE)
            # Min length 6: [larg]est->large, [round]est->round, [fre]est->free
            start = token_start(standard, 'est', 3)
            if start is not None:
                return _lm_lemma(start[:-1], [start[-1], start[-1] + 'e'], Suffix.SUPERLATIVE)
            # Min length 6: [happ]ier->happy
            start = token_start(standard, 'ier', 2)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['y'], Suffix.COMPARATIVE)
            # Min length 5: [larg]er->large, [round]er->round, [fre]er->free
            start = token_start(standard, 'er', 3)
            if start is not None and standard not in self.__adjs:
                return _lm_lemma(start[:-1], [start[-1], start[-1] + 'e'], Suffix.COMPARATIVE)

        # Verbs
        # -------------------------------------------------------------------------->

        if tag == Tag.VERB:
            # Min length 8: [picn]icking->picnic
            start = token_start(standard, 'icking', 2)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['ic'], Suffix.PROGRESSIVE)
            # Min length 7: [picn]icked->picnic
            start = token_start(standard, 'icked', 2)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['ic'], Suffix.PAST)
            # Min length 7: [formatt]ing->format, [roll]ing->roll
            start = token_start(standard, 'ing', 4)
            if start is not None:
                endings = vowel_double_consonant_endings(start)
                if endings is not None:
                    return _lm_lemma(start[:-2], endings, Suffix.PROGRESSIVE)
            # Min length 6: [bark]ing->bark, [bak]ing->bake, [free]ing->free, [dye]ing->dye, [singe]ing->singe
            start = token_start(standard, 'ing', 3)
            if start is not None:
                return _lm_lemma(start[:-1], [start[-1], start[-1] + 'e'], Suffix.PROGRESSIVE)
            # Min length 6: [picn]icks->picnic
            start = token_start(standard, 'icks', 2)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['ic'], Suffix.THIRD_PERSON)
            # Min length 6: [formatt]ed->format, [roll]ed->roll
            start = token_start(standard, 'ed', 4)
            if start is not None:
                endings = vowel_double_consonant_endings(start)
                if endings is not None:
                    return _lm_lemma(start[:-2], endings, Suffix.PAST)
            # Min length 5: [part]ied->party
            start = token_start(standard, 'ied', 2)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['y'], Suffix.PAST)
            # Min length 4: [part]ies->party, [l]ies->lie
            start = token_start(standard, 'ies', 1)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['y', 'ie'], Suffix.THIRD_PERSON)
            # Min length 4: [bark]ed->bark, [bak]ed->bake, [fre]ed->free, [dy]ed->dye, [sing]ed->singe
            start = token_start(standard, 'ed', 2)
            if start is not None:
                return _lm_lemma(start[:-1], [start[-1], start[-1] + 'e'], Suffix.PAST)
            # Min length 4: [bake]s->bake, [fre]es->free
            start = token_start(standard, 'es', 2)
            if start is not None:
                return _lm_lemma(start[:-1], [start[-1], start[-1] + 'e'], Suffix.THIRD_PERSON)
            # Min length 3: [bark]s->bark
            start = token_start(standard, 's', 2)
            if start is not None:
                return _lm_lemma(start[:-1], [start[-1]], Suffix.THIRD_PERSON)

        # NOUNS
        # -------------------------------------------------------------------------->

        if tag == Tag.NOUN:
            # Min length 6: [criteri]a->criterion
            start = token_start(standard, 'a', 5)
            if start is not None:
                return _lm_lemma(start, ['on'], Suffix.PLURAL)
            # Min length 6: [th]ieves->thief
            start = token_start(standard, 'ieves', 1)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['ief'], Suffix.PLURAL)
            # Min length 5: [nucle]i->nucleus
            start = token_start(standard, 'i', 4)
            if start is not None:
                return _lm_lemma(start, ['us'], Suffix.PLURAL)
            # Min length 5: [ber]ies->berry, [talk]ies->talkie
            start = token_start(standard, 'ies', 2)
            if start is not None:
                if ends_with_consonant(start):
                    return _lm_lemma(start, ['y', 'ie'], Suffix.PLURAL)
            # Min length 5: [wi]ves->wife, [wol]ves->wolf
            start = token_start(standard, 'ves', 2)
            if start is not None:
                return _lm_lemma(start, ['f', 'fe', 've'], Suffix.PLURAL)
            # Min length 5: [wo]men->woman
            start = token_start(standard, 'men', 2)
            if start is not None:
                return _lm_lemma(start, ['man'], Suffix.PLURAL)
            # Min length 4: [fox]es->fox, [ax]es->axe, [analys]es->analysis
            start = token_start(standard, 'es', 2)
            if start is not None:
                return _lm_lemma(start[:-1], [start[-1], start[-1] + 'e', start[-1] + 'is'], Suffix.PLURAL)
            # Min length 3: [gamer]s->gamer
            start = token_start(standard, 's', 2)
            if start is not None and not any([standard.endswith('ss'), self.__lm.has_ngram(standard + 'es')]):
                return _lm_lemma(start[:-1], [start[-1]], Suffix.PLURAL)

        # ALREADY A LEMMA
        # -------------------------------------------------------------------------->

        return standard, None

    def __best_candidate(self, stem, endings, tag):
        """Consults language model to return the best token"""
        if len(endings) == 1:
            candidate = stem + endings[0]
            if self.__lm.has_ngram(candidate):
                return candidate
            return None
        if tag == Tag.VERB:
            tokens_before = ['i', 'you', 'we', 'they', 'may', 'might', 'can', 'could', 'would', 'should']
        else:
            tokens_before = [stem + ending for ending in endings]
        candidates = [stem + ending for ending in endings]
        best_ngram = self.__lm.best_ngram(
            *[' '.join([token, candidate]) for candidate in candidates for token in tokens_before])
        if best_ngram is not None:
            return best_ngram.split()[-1]
        return self.__lm.best_ngram(*candidates)

    def __irregular_lemma(self, standard, tag):
        """Consults flat files for irregular inflections"""
        if tag == Tag.NOUN:
            if standard in self.__plural_lemma:
                # Also contain plurals of flat nouns (e.g. "hot dogs" => "hot dog")
                return self.__plural_lemma[standard], Suffix.PLURAL
        if tag == Tag.VERB:
            if standard in self.__pp_lemma:
                return self.__pp_lemma[standard], Suffix.PAST
            if standard in self.__preterit_lemma:
                return self.__preterit_lemma[standard], Suffix.PAST
        if tag == Tag.ADJ:
            if standard in self.__comparative_lemma:
                return self.__comparative_lemma[standard], Suffix.COMPARATIVE
            if standard in self.__superlative_lemma:
                return self.__superlative_lemma[standard], Suffix.SUPERLATIVE
        return None
