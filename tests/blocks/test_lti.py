import control
import numpy as np

import sigflow

def test_lti():
    """Test LTI blocks"""
    tf = control.ss2tf(control.rss(20, 1, 1, strictly_proper=True))
    s = control.tf("s")
    tf_notproper = s
    tf_unstable = 1/(s-1)
    ## test excpetion catching
    try:
        sigflow.blocks.LTI(tf=1, dt=1)
        raise
    except TypeError:
        pass
    try:
        sigflow.blocks.LTI(tf=tf_notproper, dt=1)
        raise
    except ValueError:
        pass
    try:
        sigflow.blocks.LTI(tf=tf_unstable, dt=1)
        raise
    except ValueError:
        pass
    fs = 128
    dt = 1/fs
    t_final = 10
    t = np.linspace(0, t_final, fs*t_final)
    np.random.seed(123)
    u = np.random.normal(0, 1, len(t))
    sigflow_tf = sigflow.blocks.LTI(tf=tf, dt=dt)
    yd = np.zeros_like(u)
    for i in range(len(u)):
        yd[i] = sigflow_tf(u[i])
    #TODO How to check if the output is expected??
