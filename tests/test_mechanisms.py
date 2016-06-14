
import pytest

from graphiit import micro_mechanisms as m

# TODO: test remaining gates

def check(mechanism, expected):
    """Check that the mechanism gives the expected results."""
    for inputs, output in expected.items():
        assert(mechanism(inputs) == output)


def test_AND():
    check(m.AND, {
        (0, 0): False,
        (0, 1): False,
        (1, 0): False,
        (1, 1): True,
    })


def test_OR():
    check(m.OR, {
        (0, 0): False,
        (0, 1): True,
        (1, 0): True,
        (1, 1): True,
    })


def test_COPY():
    check(m.COPY, {
        (0,): False,
        (1,): True,
    })
    # Can only have one input
    with pytest.raises(AssertionError):
        m.COPY((0, 1))


def test_NOT():
    check(m.NOT, {
        (0,): True,
        (1,): False,
    })
    # Only one input allowed
    with pytest.raises(AssertionError):
        m.NOT((0, 1))


def test_XOR():
    check(m.XOR, {
        (0, 0): False,
        (0, 1): True,
        (1, 0): True,
        (1, 1): False,
        (0, 1, 0): True,
        (1, 0, 1): False,
        (1, 1, 1): True,
    })


def test_MAJORITY():
    check(m.MAJORITY, {
        (0, 0): False,
        (0, 1): False,
        (1, 0): False,
        (1, 1): True,
        (0, 1, 0): False,
        (1, 0, 1): True,
        (1, 1, 1): True,
    })
