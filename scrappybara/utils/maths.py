import numpy as np


def xnor(*bools):
    """Takes first 2 elements and calc xnor, then use result to calc xnor with 3rd element etc"""
    result = bools[0] == bools[1]
    for b in bools[2:]:
        result = result == b
    return result


def cosine(vector_1, vector_2):
    """
    Calculates cosine similarity between 2 sparse vectors.
    A sparse vector is a dictionary of idx => non_zero_value.
    """
    numerator = 0
    for idx_1, value_1 in vector_1.items():
        if idx_1 in vector_2:
            numerator += value_1 * vector_2[idx_1]

    def _norm(_v):
        return np.sqrt(sum([x ** 2 for x in _v.values()]))

    denominator = _norm(vector_1) * _norm(vector_2)
    if denominator == 0:
        return -1
    return numerator / denominator
