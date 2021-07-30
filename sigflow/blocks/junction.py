"""Summing junction ``block''
"""
from .base import Block


class Junction(Block):
    """A summing junction class
    """
    def __init__(self, signs="++", label=None):
        """Constructor

        Parameters
        ----------
        signs : str, optional
            Signs of the inputs.
            Defaults to "++".
        label : str, optional
            Label of this junction
            Defaults to None.
        """
        super().__init__(label=label)
        self.signs = signs
