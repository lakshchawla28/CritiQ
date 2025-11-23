"""
Utility functions for the recommendation engine.
"""

import numpy as np


def normalize_matrix(matrix):
    """
    Normalize each row vector of a matrix to unit length.

    Avoids division by zero by replacing zero-norm rows with 1.
    """
    norm = np.linalg.norm(matrix, axis=1, keepdims=True)
    norm[norm == 0] = 1  # Prevent division by zero
    return matrix / norm

