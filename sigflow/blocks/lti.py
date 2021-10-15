"""A linear time invariant system block.
"""
import control
import numpy as np
import scipy

from .base import Block


class LTI(Block):
    """An LTI system class

    Parameters
    ----------
    tf : control.TransferFunction
        The transfer function representation of the LTI system.
    dt : float
        The sampling time in seconds.
    label : str, optional
        Label for this filter.
        Defaults to None.
    """
    def __init__(self, tf, dt, label=None):
        """Constructor

        Parameters
        ----------
        tf : control.TransferFunction
            The transfer function representation of the LTI system.
        dt : float
            The sampling time in seconds.
        label : str, optional
            Label for this filter.
            Defaults to None.
        """
        self._tf = None
        self._dt = None
        self._t = np.zeros(2)  # Dummy. Passed to control.forced_response
        
        self._state_vector = None  # States. Size depends on the system.
        self._state_vector_now = None # States now.
        # self._state_vector: States passed to control.passed response.
        # This is set to self._state_vector_now when new self.input is set.
        # self._state_vector_now: Contains the states returned from
        # control.forced_response
        
        self._input = 0
        self._input_vector = np.zeros(2)  # Past input and current input buffer
        self.tf = tf
        self.dt = dt
        super().__init__(label=label)
    
    @property
    def tf(self):
        """The transfer function represenstation of the LTI system"""
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
        self._state_space = control.tf2ss(_tf)
        n_states = len(self._state_space.A[1])
        # n_states = np.shape(self._state_space)[1]
        self._state_vector = np.zeros(n_states)
        # print(self._state_vector)
    
    @property
    def dt(self):
        """Sampling time"""
        return self._dt
    
    @dt.setter
    def dt(self, _dt):
        self._dt = _dt
        self._t[1] = _dt

    @property
    def input(self):
        """Input of the LTI system"""
        return self._input
   
    @input.setter
    def input(self, _input):
        """input.setter
        
        Parameters
        ----------
        _input : float
            Input to the LTI system.
        """
        self._input_vector[0] = self.input
        self._input = _input
        self._input_vector[1] = _input
        if self._state_vector_now is not None:
            self._state_vector = self._state_vector_now
        #FIXME if self.input is changed multiple times before calling
        #self._i2o, it's gonna act funny since the state vector doesn't
        #change but the input vector changed.

    def _i2o(self):
        """Pass value through the LTI system and returns the output
        
        Returns
        -------
        float
            The output of the LTI system.
        """
        #TODO Add functionality to check if the execution time
        #exceeds the sampling time self.dt.
        _, y, x = control.forced_response(
            self._state_space, U=self._input_vector, T=self._t,
            X0=self._state_vector, return_x=True)
        self._state_vector_now = x[:, 1]
        output = y[-1]
        return output
