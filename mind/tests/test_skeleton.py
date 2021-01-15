# -*- coding: utf-8 -*-

import pytest

from mind.skeleton import fib

__author__ = "Jonas Lima"
__copyright__ = "Jonas Lima"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
