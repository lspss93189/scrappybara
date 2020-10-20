import re

from scrappybara.preprocessing.sanitization import sanitize


class Tokenizer(object):
    """Rule based tokenizer, using precompiled regex patterns"""

    # SANITIZATION
    # -------------------------------------------------------------------------->

    __re_sanitization = [
        (re.compile(r'[‘’′]'), "'"),
        (re.compile(r'[“”″]'), '"'),
        (re.compile(r'[–—]+'), ' - '),
    ]

    # NON-SPLITABLE TEXT
    # -------------------------------------------------------------------------->

    # Unambiguous patterns for text that can't be split
    __re_protect = [
        re.compile(r"\s'n'\s", re.I),  # Abbreviation for "and"
        re.compile(r"\s('n|n')\s", re.I),  # Abbreviations for "and" (shorter than above)
        re.compile(r'(https?://|www\.)[^\s.]+(\.[^\s.]+)+(/[^\s]*)*', re.I),  # URLs
        re.compile(r'[^\s.]+(\.[^\s.]+)+/[^\s]*', re.I),  # URLs (shorter than above)
        re.compile(r'([:;]-?\))|([:;]-?\()', re.I),  # Common smileys
    ]

    # NON-SPLITABLE CHARS
    # -------------------------------------------------------------------------->

    __nsd = '_NSD_'  # for a dot
    __re_no_split_dot = re.compile(r'%s' % __nsd)
    __nsge = '_NSGE_'  # for '>='
    __re_no_split_gte = re.compile(r'%s' % __nsge)
    __nsle = '_NSLE_'  # for '<='
    __re_no_split_lte = re.compile(r'%s' % __nsle)
    __rnsge = '_RNSGE_'  # for '=>'
    __re_no_split_rgte = re.compile(r'%s' % __rnsge)
    __rnsle = '_RNSLE_'  # for '=<'
    __re_no_split_rlte = re.compile(r'%s' % __rnsle)

    # Common abbreviations that can be followed by an uppercase letter.
    # These abbreviations must be unambiguous (can't be equal to any common word).
    # Abbreviations below are listed without their ending ".", and in lower case.
    __abbr = [
        # Age & Genders
        'm', 'mr', 'mrs', 'ms', 'sr',
        # Jobs & degrees
        'dr', 'prof', 'rev', 'gov', 'sen', 'rep',
        # Military ranks
        'lt', 'sgt',
        # Locations
        'ave', 'st',
        # Misc
        'ed', 'feat',
    ]
    __abbr_options = r'(%s)\.' % '|'.join([abbr for abbr in __abbr])

    # Patterns that analyze the surrounding context of a single symbol to protect parts from splitting
    __re_no_split = [
        # Dots
        (re.compile(r'\.(?=\s[a-z])'), __nsd),  # Dot followed by space and lower case letter
        (re.compile(r'\.(?=\s?[,:;?!])'), __nsd),  # Dot followed by punctuation
        (re.compile(r'\.(?=\s\d+\b)'), __nsd),  # Dot followed by a digit
        (re.compile(r'\b%s(?=\s[A-Z])' % __abbr_options, re.I), r'\g<1>%s' % __nsd),  # Common abbreviation
        # Quotes
        (re.compile(r'(?<=\s)(\d[\d,.]*)\'(\d[\d,.]*)"', re.I), r'\g<1>ft\g<2>in'),  # Inches and feet
        (re.compile(r'(?<=\s)(\d[\d,.]*)\'', re.I), r'\g<1>ft'),  # Feet
        (re.compile(r'(?<=\s)(\d[\d,.]*)"', re.I), r'\g<1>in'),  # Inches
        # < and >
        (re.compile(r'\s?>\s?=\s?', re.I), __nsge),  # >=
        (re.compile(r'\s?<\s?=\s?', re.I), __nsle),  # <=
        (re.compile(r'\s?=\s?>\s?', re.I), __rnsge),  # =>
        (re.compile(r'\s?=\s?<\s?', re.I), __rnsle),  # =<
    ]

    # CHARS TO ALWAYS SEGMENT OFF
    # -------------------------------------------------------------------------->

    __re_always_split = re.compile(r'([.?!]{2,}|…+|=+|!+|\?+|"+|;+|\|+|\\+|\(+|\)+|{+|}+|\[+|]+|–+)')

    # DOTS
    # They cause issues because of abbreviations and acronyms.
    # We protect some tokens first, then seperate remaining dots in a token.
    # -------------------------------------------------------------------------->

    # Patterns that protect a single token from splitting
    # Full match
    __re_token_nosplit_dot = [
        re.compile(r'(\w\.){2,}', re.I),  # Any series of dotted single chars: "f.f.f."
        re.compile(r'\.?([^.]+\.){2,}[^.]+', re.I),  # Any series of dotted words: "asdf.asdfadsf.asdf"
        re.compile(r'[a-zA-Z]\.', re.I),  # Single char followed by a dot: "A. Gray"
        re.compile(r'\d\.(?=(\s[^A-Z]))', re.I),  # Single digit followed by a dot (the number doesn't need the dot)
        re.compile(r'(\d+\.){2,}', re.I),  # Series of numbers and dots
        re.compile(r'\.{2,}', re.I),  # Multiple dots
    ]

    # Split dots in a token
    # Partial match
    __re_token_split_dot = [
        (re.compile(r'([a-z]+)(\.)([A-Z\'])'), r'\g<1> \g<2> \g<3>'),
        (re.compile(r'\.$'), r' \g<0>'),
    ]

    # TEXT TO SEGMENT OFF ACCORDING TO CONTEXT
    # -------------------------------------------------------------------------->

    __re_segment_off = [
        # Special words to split
        (re.compile(r'(?<=\b)(can)(not)(?=\b)', re.I), r'\g<1> \g<2>'),
        # Star *
        (re.compile(r'(?<=[a-z])\*+(?=[a-z])', re.I), ' * '),
        # Plus +
        (re.compile(r'(?<=[a-z][a-z][a-z])\+(?=[a-z]{3,})', re.I), ' + '),
        (re.compile(r'(\d+)\+(?=[a-z])', re.I), r'\g<1>+ '),
        # Ampercase &
        (re.compile(r'(?<=\b)&(?!\b)'), ' & '),
        (re.compile(r'(?<!\b)&(?=\b)'), ' & '),
        (re.compile(r'([a-zA-Z][a-z]{2,})&([a-zA-Z][a-z]{2,})'), r'\g<1> & \g<2>'),
        # Slash /
        (re.compile(r'(?<=[a-z\d][a-z])/', re.I), ' / '),
        (re.compile(r'/(?=[a-z][a-z\d])', re.I), ' / '),
        # Percentage %
        (re.compile(r'(?<=[a-z])%', re.I), ' % '),
        (re.compile(r'%(?=[a-z])', re.I), ' % '),
        # Colon :
        (re.compile(r':(?=\s|$)'), ' : '),
        (re.compile(r'(?<=\s):'), ' : '),
        (re.compile(r'([a-zA-Z][a-z]{2,}):([a-zA-Z][a-zA-Z]+)'), r'\g<1> : \g<2>'),
        (re.compile(r'([a-z]{3,}):(\d+)', re.I), r'\g<1> : \g<2>'),
        (re.compile(r'([0-9]+):([a-zA-Z]+)', re.I), r'\g<1> : \g<2>'),  # 2:Engage
        # Greater than >
        (re.compile(r'(?<!-)>'), ' > '),
        # Less than <
        (re.compile(r'<(?!-)'), ' < '),
        # Comma ,
        (re.compile(r'(?<!\d),'), ' , '),
        (re.compile(r',(?!\d)'), ' , '),
        # Single quote '
        (re.compile(r"(^|\s)'(?!s)"), " ' "),
        (re.compile(r"'(\s|$)"), " ' "),
        (re.compile(r"(?<=\w\w\w)'(?=\w\w\w)", re.I), " ' "),
        (re.compile(r"(^|\s)'(?=s\w)", re.I), " ' "),
        (re.compile(r"(n't|'re|'ll|'ve|'m|'d|'s)(?=\s|$)", re.I), r' \g<1> '),
        # Bullets (often * or -)
        (re.compile(r'\s([*-])([a-zA-Z]+)(?=\s|$)'), r' \g<1> \g<2> '),
    ]

    # TEXT TO REATTACH
    # -------------------------------------------------------------------------->

    __re_reattach = [
        (re.compile(r'\b([A-Z])\s([A-Z])\s&\s([A-Z])\b'), r'\g<1>\g<2>&\g<3>'),
        (re.compile(r'\b([A-Z])\s&\s([A-Z])\s([A-Z])\b'), r'\g<1>&\g<2>\g<3>'),
        (re.compile(r'\b([A-Z])\s&\s([A-Z])\b'), r'\g<1>&\g<2>'),
        (re.compile(r'(\.{2,}) \.'), r'\g<1>.'),
    ]

    def __call__(self, text):
        """Returns a list of tokens"""
        if not text:
            return ['']
        text = sanitize(text, self.__re_sanitization)
        # Protect tokens
        protected, text = self.__protect_text(text)
        # Protect single symbols
        for nsp in self.__re_no_split:
            text = re.sub(nsp[0], nsp[1], text)
        # Segment off unambiguous patterns
        text = re.sub(self.__re_always_split, r' \g<0> ', text)
        # Segment off ending dots
        tokens = []
        for token in text.split():
            if any([re.fullmatch(regex, token) for regex in self.__re_token_nosplit_dot]):
                tokens.append(token)
            else:
                for pattern, rep in self.__re_token_split_dot:
                    token = re.sub(pattern, rep, token)
                tokens.extend(token.split())
        text = ' '.join(tokens)
        # Segment off other symbols
        for pattern, replace in self.__re_segment_off:
            text = re.sub(pattern, replace, text)
        text = ' '.join(text.split())
        # Re-establish symbols
        text = re.sub(self.__re_no_split_dot, '.', text)
        text = re.sub(self.__re_no_split_gte, ' >= ', text)
        text = re.sub(self.__re_no_split_lte, ' <= ', text)
        text = re.sub(self.__re_no_split_rgte, ' => ', text)
        text = re.sub(self.__re_no_split_rlte, ' =< ', text)
        # Re-attach text
        for replace in self.__re_reattach:
            text = re.sub(replace[0], replace[1], text)
        # Re-establish protected patterns
        for key, value in protected.items():
            text = text.replace(key, value)
        return text.split()

    def __protect_text(self, text):
        """Detects patterns that should not be tokenized"""
        protected = {}
        index = 1
        for pattern in self.__re_protect:
            match = re.search(pattern, text)
            while match:
                token = match.group()
                key = '_PROTECTED_%d_' % index
                protected[key] = token
                text = text.replace(token, key)
                match = re.search(pattern, text)
                index += 1
        return protected, text
