"""Tests for sigflow.system.system
"""
import numpy as np
import pytest

import sigflow


@pytest.mark.parametrize("fake_block", [10, range(10), "abcd"])
def test_wrong_system_init(fake_block):
    """test System class construction"""
    ## catch exception when passing non iterable of block object.
    Sys = sigflow.System
    with pytest.raises(TypeError):
        sys = Sys(fake_block)


@pytest.fixture
def random_matrix_blocks():
    """Returns a random amount of matrix blocks."""
    n = np.random.randint(20, 100)
    matrixes = np.random.random((n,3,4))
    matrix_blocks = [sigflow.Matrix(m, label="m%d" % i)
                     for i, m in enumerate(list(matrixes))]
    return matrix_blocks


def test_correct_system_init(random_matrix_blocks):
    ## correct case
    Sys = sigflow.System
    sys = Sys(random_matrix_blocks)
    actual = [sys.blocks, sys._succ]
    n = len(random_matrix_blocks)
    expected = ([dict(enumerate(random_matrix_blocks))]
                + [dict(zip(range(n), [[{}]*3]*n))])
    np.testing.assert_equal(actual, expected)


@pytest.mark.parametrize("fake_block", [10, range(10), "abcd"])
def test_wrong_add_block(fake_block):
    Sys = sigflow.System
    sys = Sys()
    with pytest.raises(TypeError):
        sys.add_blocks(fake_block)


def test_correct_add_one_block(random_matrix_blocks):
    """test adding block to the system"""
    Sys = sigflow.System
    sys = Sys()
    mat = random_matrix_blocks[0]
    sys.add_blocks(mat)
    actual = [sys.blocks, sys._succ]
    expected = [{0: mat}, {0: [{}]*3}]
    print(actual, expected)
    np.testing.assert_equal(actual, expected)


def test_correct_add_blocks(random_matrix_blocks):
    """test adding multiple blocks to the system"""
    Sys = sigflow.System
    sys = Sys()
    sys.add_blocks(random_matrix_blocks)
    n = len(random_matrix_blocks)
    actual = [sys.blocks, sys._succ]
    expected = ([dict(enumerate(random_matrix_blocks))]
                + [dict(zip(range(n), [[{}]*3]*n))])
    np.testing.assert_equal(actual, expected)


@pytest.fixture
def two_blocks_system():
    """Returns a system with two blocks"""
    Sys = sigflow.System
    m = np.random.random((2, 2))
    blocka = sigflow.Matrix(m)
    blockb = sigflow.Junction("+-")
    sys = Sys([blocka, blockb])
    return sys


@pytest.mark.parametrize("method", ["id", "obj"])
def test_change_edge(two_blocks_system, method):
    sys = two_blocks_system
    def add_remove(a, b):
        sys.add_edge(a, b, 0, 1)
        sys.add_edge(a, b, 1, 0)
        print(sys._succ)
        sys.remove_edge(a, b, 0, 1)
    if method == "id":
        add_remove(0, 1)
    if method == "obj":
        add_remove(sys.blocks[0], sys.blocks[1])
    actual = sys._succ
    print(sys._succ)
    expected = {0: [{}, {1: 0}], 1: [{}]}
    assert actual==expected


def test_clear_edges(two_blocks_system):
    sys = two_blocks_system
    sys.add_edge(0, 1, 0, 1)
    sys.add_edge(0, 1, 1, 0)
    sys.clear_edges()
    actual = sys._succ
    expected = {0: [{}]*2, 1: [{}]}
    assert actual == expected


@pytest.mark.parametrize("fake_block",
                         [10, range(10), "abcd",
                         random_matrix_blocks])
def test_wrong_remove_block(two_blocks_system, fake_block):
    with pytest.raises((TypeError, ValueError)):
        sys = two_blocks_system
        sys.remove_blocks(fake_block)


@pytest.mark.parametrize("method", ["id", "obj"])
def test_remove_blocks(two_blocks_system, method):
    """test System.remove_blocks method."""
    sys = two_blocks_system
    sys.add_edge(0, 1, 0, 1)
    sys.add_edge(0, 1, 1, 0)
    if method == "id":
        sys.remove_by_id(0)
    if method == "obj":
        sys.remove_blocks(sys.blocks[0])
    actual = [sys.blocks, sys._succ]
    expected = [{1: sys.blocks[1]},
                {1: [{}]}]
    np.testing.assert_equal(actual, expected)


def test_system():
    m = np.random.random((2, 2))
    blocka = sigflow.Matrix(m)
    blockb = sigflow.Junction("+-")
    Sys = sigflow.System
    sys = Sys([blocka, blockb])
    sys.add_edge(0, 1, 0, 1)
    sys.add_edge(0, 1, 1, 0)
    sys.set_ninout(2, 1)
    sys.add_edge("input", 0, 0, 0)
    sys.add_edge("input", 0, 1, 1)
    sys.add_edge(1, "output", 0, 0)

    ## test input to output
    input_data = [4, 5]
    out = sys(input_data)
    actual = out[0]
    res = np.array([[-1, 1]]) @ m @ np.array(input_data).reshape((-1, 1))
    expected = res[0]
    np.testing.assert_allclose(actual, expected)


@pytest.mark.parametrize("data, expected",
                         [[1, [1,0]],
                          [[np.ones(3)], [np.ones(3), np.zeros(3)]]])
def test_feedback(data, expected):
    block = sigflow.Junction("+-")
    sys = sigflow.System(block, nin=1, nout=1)
    sys.add_edge("input", block)
    sys.add_edge(block, block, 0, 1)
    sys.add_edge(block, "output")
    res = []
    for _ in range(2):
        print("data: ", data)
        res.append(sys(data)[0])
    np.testing.assert_equal(res, expected)

# def test_str(two_blocks_system):
#     sys = two_blocks_system



