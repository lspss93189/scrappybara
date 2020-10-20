from scrappybara.utils.text import starts_with_uppercase_letter, has_only_letters


def _valid_ngram_token(token):
    # Edge cases
    if not token:
        return False
    if token == 'I':
        return True
    # Validate
    if any([not has_only_letters(token), starts_with_uppercase_letter(token)]):
        return False
    return True


def _valid_tokens(tokens):
    return all([_valid_ngram_token(token) for token in tokens])


def extract_ngrams(token_lists, order):
    """Extracts ngram from left to right"""
    ngrams = []
    for token_list in token_lists:
        if order == 1:
            ngrams_tokens = [[token] for token in token_list]
        else:
            ngrams_tokens = [ngram_tokens for ngram_tokens in zip(*[token_list[i:] for i in range(order)])]
        filtered_ngrams = [' '.join(ngram_tokens) for ngram_tokens in ngrams_tokens if _valid_tokens(ngram_tokens)]
        ngrams.extend([ngram.lower() for ngram in filtered_ngrams])
    return ngrams
