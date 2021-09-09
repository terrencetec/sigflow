"""A filter block.
"""
import control
import numpy as np
import scipy

from .base import Block


class Filter(Block):
    """A Filter block class

    This is simply a single-input-single-output LTI system defined by a
    single TransferFunction object.

    Parameters
    ----------
    tf : control.TransferFunction
        The transfer function of the filter (continuous).
    fs : float
        Sampling frequency in Hz.
    method : str, optional
        Method used to convert the continuous system to
        discrete system.
        Argument is passed to ``scipy.signal.cont2discrete``.
        Defaults to "bilinear".
    label : str, optional
        Label for this filter.
        Defaults to None.

    Note
    ----
    When ``inputs.setter`` the current input and output is saved into a register
    for next cycle.
    This means that calling ``inputs.setter`` indicates the end of a cycle.
    """
    def __init__(self, tf, fs, method="bilinear", label=None):
        """Constructor

        Parameters
        ----------
        tf : control.TransferFunction
            The transfer function of the filter (continuous).
        fs : float
            Sampling frequency in Hz.
        method : str, optional
            Method used to convert the continuous system to
            discrete system.
            Argument is passed to ``scipy.signal.cont2discrete``.
            Defaults to "bilinear".
        label : str, optional
            Label for this filter.
            Defaults to None.
        """
        self._tf = None
        self._fs = None
        self._method = None
        self._num_d = None
        self._den_d = None
        self._input_register = None
        self._output_register = None
        self.tf = tf
        self.fs = fs
        self.method = method
        super().__init__(label=label)

    def _i2o(self):
        """Pass input through filter and return the output"""
        input_register = self.input_register
        output_register = self.output_register
        num_d = self.num_d
        den_d = self.den_d
        out = (np.dot(num_d, input_register)
               - np.dot(den_d[1:], output_register[1:]))
        return out

    @property
    def inputs(self):
        """Input of the block."""
        return self._inputs

    @inputs.setter
    def inputs(self, _inputs):
        """input.setter"""
        self._latch_output_register()
        self._inputs = _inputs
        self._latch_input_register()

    @property
    def tf(self):
        """The transfer function of the filter (continuous)."""
        return self._tf

    @tf.setter
    def tf(self, _tf):
        """tf.setter"""
        if not isinstance(_tf, control.TransferFunction):
            raise TypeError("tf must be a TransferFunction object.")
        if len(_tf.zero()) > len(_tf.pole()):
            raise ValueError("tf must be a proper transfer function.")
        if np.any(_tf.pole().real >= 0):
            raise ValueError("tf must be a stable transfer function.")

        self._tf = _tf
        self._set_coefs()
        self._reset_register()

    @property
    def fs(self):
        """Sampling frequency in Hz"""
        return self._fs

    @fs.setter
    def fs(self, _fs):
        """fs.setter"""
        self._fs = _fs
        self._set_coefs()
        self._reset_register()

    @property
    def method(self):
        """Method used to convert the continuous system discrete system."""
        return self._method

    @method.setter
    def method(self, _method):
        """method.setter"""
        self._method = _method
        self._set_coefs()
        self._reset_register()

    @property
    def num_d(self):
        """Discrete transfer function numerators"""
        return self._num_d

    @num_d.setter
    def num_d(self, _num_d):
        """num_d.setter"""
        self._num_d = _num_d

    @property
    def den_d(self):
        """Discrete transfer function denominator"""
        return self._den_d

    @den_d.setter
    def den_d(self, _den_d):
        """den_d.setter"""
        self._den_d = _den_d

    @property
    def input_register(self):
        """Input register (history of the input)"""
        return self._input_register

    @input_register.setter
    def input_register(self, _input_register):
        """input_register.setter"""
        self._input_register = _input_register

    @property
    def output_register(self):
        """output register (history of the output)"""
        return self._output_register

    @output_register.setter
    def output_register(self, _output_register):
        """input_register.setter"""
        self._output_register = _output_register

    def _set_coefs(self):
        """Set discrete filter coefficients."""
        if (self.tf is not None
            and self.fs is not None
            and self.method is not None):
            # Set coefficients for discrete filters.
            # Note: H(z) = (b0 + b1*z^1...)/(1 + a1*z^1...)
            # print("set coefs")
            num = self.tf.num[0][0]
            den = self.tf.den[0][0]
            dt = 1/self.fs
            method = self.method
            num_d, den_d, _ = scipy.signal.cont2discrete(
                (num, den), dt=dt, method=method)
            num_d = num_d.reshape(-1)
            den_d = den_d.reshape(-1)
            self.num_d = num_d
            self.den_d = den_d

    def _reset_register(self):
        """Reset the input/output register"""
        if self.num_d is not None and self.den_d is not None:
            self.input_register = np.zeros_like(self.num_d)
            self.output_register = np.zeros_like(self.den_d)

    def _latch_input_register(self):
        """Shift and then put input value into input register
        """
        if self.input_register is not None:
            self.input_register[1:] = self.input_register[:-1]
            self.input_register[0] = self.inputs

    def _latch_output_register(self):
        """Shift and then put input value into input register
        """
        if self.output_register is not None:
            self.output_register[0] = self.output
            self.output_register[1:] = self.output_register[:-1]
