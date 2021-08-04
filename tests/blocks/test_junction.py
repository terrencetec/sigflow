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
    input = np.array([1, 2, 3])
    ## Catch exception when input size is not equal to that of no. of rows.
    try:
        junction(input)
        print("Exception not catched")
        raise
    except ValueError:
        pass

    ## test input-output relationship
    input = np.random.random(4)
    correct_output = np.array([input[0] - input[1] - input[2] + input[3]])
    output = junction(input)
    assert np.array_equal(output, correct_output)
