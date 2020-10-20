import re

from scrappybara.preprocessing.sanitization import sanitize
from scrappybara.preprocessing.tokenizer import Tokenizer


class Sentencizer(object):
    """Splits text into tokens grouped by sentences"""

    __re_newline = re.compile(r'\s*[\t\n\r]+\s*')
    __re_quote = re.compile(r'".*?"')
    __re_bracket = re.compile(r'\(.*?\)')
    __re_multi_spaces = re.compile(r'\s+')
    __re_quote_block_start = '༺'
    __re_quote_block_end = '༻'
    __re_bracket_block_start = '⦅'
    __re_bracket_block_end = '⦆'
    __re_sent_enders = re.compile(r'([.?!:]+|¶)')
    __re_sanitization = [
        (re.compile(r'\."'), '."¶'),  # The end dot of a sentence can be in quote
    ]

    def __init__(self):
        self.__tokenize = Tokenizer()

    def __call__(self, text):
        """Returns a list of lists of tokens"""
        quotes = []
        brackets = []

        def _insert_quote_block(_token, _ctr):
            _ctr.append('"')
            _ctr.extend(self.__tokenize(quotes[int(_token[1:-1])]))
            _ctr.append('"')

        blocks = re.split(self.__re_newline, text)
        blocks = [sanitize(block, self.__re_sanitization) for block in blocks]
        blocks = [
            self.__find_blocks(block, quotes, self.__re_quote, self.__re_quote_block_start, self.__re_quote_block_end)
            for block in blocks]
        blocks = [self.__find_blocks(block, brackets, self.__re_bracket, self.__re_bracket_block_start,
                                     self.__re_bracket_block_end) for block in blocks]
        token_lists = []
        for block in blocks:
            tokens = self.__tokenize(block)
            for sent_tokens in self.__split_sentences(tokens):
                sent_tokens_with_blocks = []
                for token in sent_tokens:
                    if token.startswith(self.__re_quote_block_start):
                        _insert_quote_block(token, sent_tokens_with_blocks)
                    elif token.startswith(self.__re_bracket_block_start):
                        idx = int(token[1:-1])
                        sent_tokens_with_blocks.append('(')
                        for nested_token in self.__tokenize(brackets[idx]):
                            if nested_token.startswith(self.__re_quote_block_start):
                                _insert_quote_block(nested_token, sent_tokens_with_blocks)
                            else:
                                sent_tokens_with_blocks.append(nested_token)
                        sent_tokens_with_blocks.append(')')
                    else:
                        sent_tokens_with_blocks.append(token)
                token_lists.append(sent_tokens_with_blocks)
        return token_lists

    def __find_blocks(self, text, ctr, pattern, block_starter, block_ender):
        shift = 0
        for quote, sidx, eidx in [(m.group(), m.start(), m.end()) for m in re.finditer(pattern, text)]:
            ctr.append(quote[1:-1])
            number = str(len(ctr) - 1)
            text = text[:sidx - shift] + ' ' + block_starter + number + block_ender + ' ' + text[eidx - shift:]
            shift += len(quote) - 4 - len(number)
        return re.sub(self.__re_multi_spaces, ' ', text)

    def __contains_block(self, tokens):
        for token in tokens:
            if self.__re_quote_block_start in token or self.__re_bracket_block_start in token:
                return True
        return False

    def __split_sentences(self, tokens):
        sents = []
        current_sent = []
        for token in tokens:
            if re.fullmatch(self.__re_sent_enders, token):
                if token != '¶':
                    current_sent.append(token)
                sents.append(current_sent)
                current_sent = []
            else:
                current_sent.append(token)
        if current_sent:
            sents.append(current_sent)
        return sents
