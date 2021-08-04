"""Tests for sigflow.blocks.matrix
"""
import numpy as np
import sigflow.blocks.matrix


def test_matrix():
    """Test sigflow.blocks.base.Matrix"""
    matrix = sigflow.blocks.matrix.Matrix(label="test")
    ## Catch exception when matrix is not defined.
    try:
        matrix.matrix
        print("Exception not catched")
        raise
    except ValueError:
        pass

    a = np.array([1])
    ## Catch exception when passing non-matrix
    try:
        matrix.matrix = a
        print("Exception not catched")
        raise
    except ValueError:
        pass

    a = np.random.random((2, 3))
    matrix = sigflow.blocks.matrix.Matrix(a, label="test")
    input = np.array([1])
    ## Catch exception when input size is not equal to that of no. of rows.
    try:
        matrix(input)
        print("Exception not catched")
        raise
    except ValueError:
        pass

    ## test input-output relationship
    input = np.random.random(3)
    correct_output = a @ input
    output = matrix(input)
    assert np.array_equal(output, correct_output)
