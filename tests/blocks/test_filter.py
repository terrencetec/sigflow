"""Tests for sigflow.blocks.filter.
"""
import control
import numpy as np
import matplotlib.pyplot as plt
import scipy

import sigflow.blocks.filter


def test_filter():
    s = control.tf("s")
    # tf = 2*np.pi/(s+2*np.pi) * 3.14  # Simple low-pass at 1Hz with 3.14 static gain

    tf = (s**2 + 2*s + 1)/(s**3 + 5*s**2 + 5*s + 10)
    num = tf.num[0][0]
    den = tf.den[0][0]


    fs = 128  # 128 Hz
    dt = 1/fs

    num_d, den_d, _ = scipy.signal.cont2discrete((num, den), dt=dt, method="bilinear")
    num_d = num_d[0]
    # den_d = den_d[0]

    t = np.linspace(0, 1024, fs*1024)
    np.random.seed(123)
    u = np.random.normal(1, 1, len(t))
    # _, y = control.forced_response(tf, U=u, T=t)
    filter_ = sigflow.blocks.Filter(tf, fs=fs)

    yd = np.zeros_like(u)
    y_sigflow = np.zeros_like(u)
    u_buffer = np.zeros_like(num_d)
    y_buffer = np.zeros(len(den_d)-1)

    for i in range(len(u)):
        u_buffer[0] = u[i]
        y_now = np.dot(num_d, u_buffer) - np.dot(den_d[1:], y_buffer)
    #     if i == 0:
    #         y_now = 0
        yd[i] = y_now

        u_buffer[1:] = u_buffer[:-1]  # right shift
        y_buffer[1:] = y_buffer[:-1]

        y_buffer[0] = y_now
        y_sigflow[i] = filter_(u[i])

    assert np.array_equal(y_sigflow, yd)
