"""
Cosine similarity functions
"""

import numpy as np
from .utils import normalize_matrix


def cosine_similarity(matrix):
    """
    Compute cosine similarity between all rows of matrix.
    matrix = users x movies rating matrix
    """
    matrix_norm = normalize_matrix(matrix)
    return matrix_norm @ matrix_norm.T
