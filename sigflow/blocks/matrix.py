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
        self.matrix = np.array(matrix)
        if len(self.matrix.shape) != 2:
            raise ValueError("matrix must be a 2-D array.")
        self.ninput, self.noutput = self.matrix.shape
        self.n
