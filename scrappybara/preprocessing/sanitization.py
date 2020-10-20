import re


def sanitize(text, patterns_replacements):
    """Arg patterns_replacements is a list of tuples (regex pattern, string to replace the match with)"""
    try:
        text = text.strip()
        for rep in patterns_replacements:
            text = re.sub(rep[0], rep[1], text)
        return ' '.join(text.split())
    except (AttributeError, KeyError):
        return ''
