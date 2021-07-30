"""A filter block.
"""
from .base import Block


class Filter(Block):
    """A Filter block class

    This is simply a single-input-single-output LTI system defined by a
    single TransferFunction object.
    """
    def __init__(self, tf, label=None):
        """Constructor

        Parameters
        ----------
        tf : control.TransferFunction
            The transfer function of the filter (continuous).
        label : str, optional
            Label for this filter.
            Defaults to None.
        """
        super().__init__(label=label)
        self.tf = tf
