"""
"""
import sigflow.helloworld
import sigflow.clitools


def test_helloworld():
    string = sigflow.helloworld.helloworlds(1)
    assert string == 'Hello World!'
