# -*- coding: utf-8 -*-
import pytest

from dharma.utils.inspect import get_all_subclasses


class A(object):
    pass


class B1(A):
    pass


class B2(A):
    pass


class C(B1):
    pass


class D(C, B2):
    pass


@pytest.mark.parametrize("cls,expected", [
    (A, {D, C, B1, B2}),
    (B1, {D, C}),
    (C, {D}),
    (D, set())
], ids=["A", "B1", "C", "D"])
def test_get_all_subclasses(cls, expected):
    assert expected == get_all_subclasses(cls)
