"""Matrix block
"""
from .base import Block


class Matrix(Block):
    """A Matrix class
    """
    def __init__(self, matrix, label=None):
        """Constructor

        Parameters
        ----------
        matrix : array
            The matrix.
        label : str, optional
            Label of this matrix
            Defaults to None.
        """
        super().__init__(label=label)
        self.matrix = matrix
