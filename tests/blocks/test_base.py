"""Tests for sigflow.blocks.base
"""
import numpy as np
import sigflow.blocks.base


def test_block():
    """Test sigflow.blocks.base.Block"""
    block = sigflow.blocks.base.Block(label="test")
    random_number = np.random.random()
    output = block(random_number)
    assert output == random_number
