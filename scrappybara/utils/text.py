import re

LETTERS = set('abcdefghijklmnopqrstuvwxyz')
CONSONANTS = set('qwrtpsdfghjklzxcvbnm')
VOWELS = set('eyuioa')
DIGITS = set('0123456789')

UPPERCASE_LETTERS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

_RE_ONLY_LETTERS = re.compile(r'[a-zA-Z]+')
_RE_ONLY_DIGITS = re.compile(r'\d+')
_RE_SPECIAL_CHAR = re.compile(r'[`~!@#$%^&*()\-_=+\[\]{}\\|;:\'",.<>/?]')


# ###############################################################################
# TOKENS
# ###############################################################################


def starts_with_uppercase_letter(token):
    return token[0] in UPPERCASE_LETTERS


def ends_with_consonant(token):
    return token[-1] in CONSONANTS


def has_only_letters(token):
    return bool(re.fullmatch(_RE_ONLY_LETTERS, token))


def has_only_lowercase_letters(token):
    return bool(re.fullmatch(_RE_ONLY_LETTERS, token))


def has_only_digits(token):
    return bool(re.fullmatch(_RE_ONLY_DIGITS, token))


def has_special_char(token):
    return bool(re.findall(_RE_SPECIAL_CHAR, token))


def token_start(token, ending, start_min_length):
    """Given an ending, returns the start of a token if possible"""
    if token.endswith(ending) and len(token) > len(ending):
        start = token[:-len(ending)]
        if len(start) >= start_min_length:
            return start
    return None


def token_prefix(token, prefixes):
    """Returns prefix & base if a prefix is detected"""
    els = token.split('-')
    if len(els) == 2:
        return els[0] + '-', els[1]
    else:
        for verb_prefix in prefixes:
            if token.startswith(verb_prefix):
                return verb_prefix, token[len(verb_prefix):]
    return None


def vowel_double_consonant_endings(token):
    """When a vowel-consonant-consonant ending is detected, returns simple & double consonant endings"""
    try:
        if token[-3] in VOWELS and token[-2] in CONSONANTS and token[-2] == token[-1]:
            return [token[-1], token[-1] + token[-1]]
    except IndexError:
        return None
    return None


# ###############################################################################
# TEXT MARKING
# ###############################################################################


def functionalize(function_name, *args):
    args_str = ', '.join([str(arg) for arg in args if arg is not None])
    return str(function_name) + '(' + args_str + ')'


def defunctionalize(marked_text):
    fname, arg = marked_text.split('(')
    return fname, arg[:-1]


def associate(*args):
    return 'ǁ'.join([str(arg) for arg in args if arg is not None])


def dissociate(text):
    try:
        word_1, word_2 = text.split('ǁ')
        return word_1, word_2
    except ValueError:
        return None


def attach_attributes(token, *attrs):
    return '»'.join([str(token)] + [str(a) for a in attrs if a is not None])


def detach_attributes(text):
    return text.split('»')
