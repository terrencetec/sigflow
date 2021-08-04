"""Summing junction ``block''
"""
import numpy as np

from .matrix import Matrix


class Junction(Matrix):
    """A summing junction class

    Note
    ----
    Block diagram representation for Junction(signs="+-"):

    .. code-block::

       input 1 -> (+ -) -> output
                     ^
                     |
       input 2 -------

    Block diagram representation for Junction(signs="+-+"):

    .. code-block::

       input 1 -> (+ - +) -> output
                     ^ ^
                     | |
       input 2 ------- |
       input 3 ---------
    """
    def __init__(self, signs="++", label=None):
        """Constructor

        Parameters
        ----------
        signs : str, optional
            Signs of the inputs.
            Define the number of inputs by the len of the string.
            Only takes "+" or "-" for summing/subtrating.
            Defaults to "++".
        label : str, optional
            Label of this junction
            Defaults to None.
        """
        super().__init__(label=label)
        self.signs = signs

    @property
    def signs(self):
        """Signs of the inputs"""
        return self._signs

    @signs.setter
    def signs(self, _signs):
        """Signs setter

        Parameters
        ----------
        _signs : str
            Signs of the inputs.
            Define the number of inputs by the len of the string.
            Only takes "+" or "-" for summing/subtrating.
        """
        # Check for non "+","-" characters.
        nplus = _signs.count("+")
        nminus = _signs.count("-")
        if nplus+nminus != len(_signs):
            raise ValueError('signs can only take "+" or "-"')

        # Construct the junction as a flat matrix
        matrix = np.ones((1, len(_signs)))
        for i in range(len(_signs)):
            if _signs[i] == "-":
                matrix[0, i] = -1
        self.matrix = matrix
        self._signs = _signs
