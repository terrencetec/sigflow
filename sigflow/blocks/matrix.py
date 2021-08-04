"""Matrix block
"""
import numpy as np

from .base import Block


class Matrix(Block):
    """A Matrix class

    Attributes
    ----------
    label : str or None
        Label of this matrix
    matrix : array or None
        The matrix.
    input : array
        The input array
    output : array
        The output array
    ninput : int
        The number of inputs defined by the number of columns of the matrix.
        Calculated, can't set.
    noutput : input
        The number of outputs defined by the number of rows of the matrix.
        Calculated, can't set.
    """
    def __init__(self, matrix=None, label=None):
        """Constructor

        Parameters
        ----------
        matrix : array or None, optional
            The matrix.
            Defaults to None.
        label : str or None, optional
            Label of this matrix
            Defaults to None.
        """
        super().__init__(label=label)
        if matrix is None:
            self.matrix = None
        else:
            self.matrix = np.array(matrix)

    def _i2o(self):
        """Convert inputs to outputs via self.matrix.

        Returns
        -------
        array
            Matrix multiplication of self.matrix and self.input
            self.matrix @ self.input
        """
        if len(self.input) != self.ninput:
            raise ValueError("Number of inputs:{} doesn't match"
                             " that of the matrix:{}"
                             "".format(len(self.input), self.ninput))
        return self.matrix @ self.input

    @property
    def ninput(self):
        """Number of inputs"""
        return self.matrix.shape[1]

    @ninput.setter
    def ninput(self, ninput):
        """ninput setter (useless here)"""
        self._ninput = ninput

    @property
    def noutput(self):
        """Number of outputs"""
        return self.matrix.shape[0]

    @noutput.setter
    def noutput(self, noutput):
        """noutput setter (useless here)"""
        self._noutput = noutput

    @property
    def matrix(self):
        """The representing matrix."""
        if self._matrix is None:
            raise ValueError("self.matrix is not set, please set self.matrix"
                             " before using this block.")
        return self._matrix

    @matrix.setter
    def matrix(self, mat):
        """self.matrix setter

        Parameters
        ----------
        mat : array
            The matrix.
        """
        if mat is None:
            pass
        elif len(mat.shape) != 2:
            raise ValueError("matrix must be a 2-D array.")
        self._matrix = mat
