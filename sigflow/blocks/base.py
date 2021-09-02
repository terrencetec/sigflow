"""Elements in a block diagram
"""
class Block:
    """A general block base class

    Attributes
    ----------
    label : str or None
        Label for this block.
    inputs : float or array
        The input of this block.
    output : float or array
        The output of this block, calculated by self._i2o()
    ninput : int
        The number of inputs
    noutput : int
        The number of outputs

    Note
    ----
    Block diagram representation:

    inputs --> [block] --> output

    Call this block to use:

    .. code-block:: python

       output = block(input)
    """
    def __init__(self, label=None):
        """Constructor

        Parameters
        ----------
        label : str or None, optional
            Label for this block.
            Defaults to None
        """
        self.label = label
        self.inputs = 0.
        self.ninput = 1
        self.noutput = 1

    def __call__(self, inputs):
        """Call method

        Parameters
        ----------
        input :
            input to the block

        Returns
        -------
        self.output
        """
        self.inputs = inputs
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
        return self.inputs

    @property
    def inputs(self):
        """Input of the block."""
        return self._inputs

    @inputs.setter
    def inputs(self, inputs):
        """input setter

        Parameters
        ----------
        inputs :
            Input to the block

        Returns
        -------
            inputs
        """
        self._inputs = inputs

    @property
    def output(self):
        """Output of the block"""
        return self._i2o()

    @property
    def ninput(self):
        """Number of inputs"""
        return self._ninput

    @ninput.setter
    def ninput(self, ninput):
        """ninput setter"""
        self._ninput = ninput

    @property
    def noutput(self):
        """Number of inputs"""
        return self._noutput

    @noutput.setter
    def noutput(self, noutput):
        """noutput setter"""
        self._noutput = noutput
