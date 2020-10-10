# -*- coding: utf-8 -*-

import pytest
from twitch_helix.skeleton import fib

__author__ = "Patrick Hanford"
__copyright__ = "Patrick Hanford"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
