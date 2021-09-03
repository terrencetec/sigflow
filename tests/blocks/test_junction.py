"""Tests for sigflow.blocks.junction
"""
import numpy as np
import sigflow.blocks.junction


def test_junction():
    """Test sigflow.blocks.base.junction"""
    junction = sigflow.blocks.junction.Junction(label="test")

    signs = "+-a+"
    ## Catch exception when passing non "+", "-" characters.
    try:
        junction.signs = signs
        print("Exception not catched")
        raise
    except ValueError:
        pass

    signs = "+--+"
    junction = sigflow.blocks.junction.Junction(signs, label="test")
    inputs = np.array([1, 2, 3])
    ## Catch exception when inputs size is not equal to that of no. of rows.
    try:
        junction(inputs)
        print("Exception not catched")
        raise
    except ValueError:
        pass

    ## test inputs-output relationship
    inputs = np.random.random(4)
    correct_output = np.array([inputs[0] - inputs[1] - inputs[2] + inputs[3]])
    output = junction(inputs)
    assert np.array_equal(output, correct_output)
