"""Elements in a block diagram
"""
class Block:
    """A general block base class

    Note
    ----
    Block diagram representation

    input --> [block] --> output
    """
    def __init__(self, label=None):
        """Constructor

        Parameters
        ----------
        label : str, optional
            Label for this block.
            Defaults to None
        """
        self.label = label
        self.input = 0

    def __call__(self, input):
        """Call method

        Parameters
        ----------
        input :
            input to the block

        Returns
        -------
        self.output
        """
        self.input = input
        return self.output

    def _i2o(self):
        """Method to convert the input signal to an output signal.

        Returns
        -------
        output :
            Output of the block.
            By default, it's the same as the input

        Note
        ----
        This method should be redefined to suit other purposes.
        """
        return self.input

    @property
    def input(self):
        """Input of the block.
        """
        return self._input

    @input.setter
    def input(self, input):
        """input setter

        Parameters
        ----------
        input :
            Input to the block

        Returns
        -------
            input
        """
        self._input = input

    @property
    def output(self):
        """Output of the block
        """
        return self._i2o()
