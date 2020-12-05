from operator import setitem

import pytest

from pca.utils.collections import (
    Bunch,
    FrozenProxy,
    freeze,
    frozendict,
)


@pytest.mark.parametrize(
    "value", [None, True, False, "value", 1, 200, 2000000000, 1.15, 1 + 2j,],
)
def test_freeze_immutable(value):
    assert freeze(value) is value


@pytest.mark.parametrize(
    "value, expected",
    [
        ({}, frozendict()),
        (frozendict(), frozendict()),
        ({1: 2, "1": "2"}, frozendict({1: 2, "1": "2"})),
        (frozendict(a=1, b=2), frozendict(a=1, b=2)),
        (frozendict(a=["a", {1, 2}]), frozendict(a=("a", frozenset([1, 2])))),
        ({"a": ["a", {1, 2}]}, frozendict(a=("a", frozenset([1, 2])))),
    ],
)
def test_freeze_dict_like(value, expected):
    assert freeze(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ([], ()),
        ((), ()),
        ((e for e in ()), ()),
        ((1, 2), (1, 2)),
        ([1, 2], (1, 2)),
        ((e for e in (1, 2)), (1, 2)),
        ([set(), []], (frozenset(), ())),
        ((e for e in ([], [])), ((), ())),
    ],
)
def test_freeze_sequence(value, expected):
    assert freeze(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (set(), frozenset()),
        (frozenset(), frozenset()),
        ({1, 2}, frozenset([1, 2])),
        (frozenset([1, 2]), frozenset([1, 2])),
        ({(1, 2), frozendict(s=frozenset())}, frozenset(((1, 2), frozendict(s=frozenset())))),
    ],
)
def test_freeze_set_like(value, expected):
    assert freeze(value) == expected


class ValueClass:
    set = set()
    list = []
    dict = {}
    inner = freeze(Bunch(key=Bunch(inner_key="value")))

    not_set: set

    @property
    def property_simple_value(self):
        return []

    @property
    def property_inner_value(self):
        return Bunch(key=Bunch(inner_key="value"))

    def method(self, arg):
        return arg


def test_frozen_proxy_types():

    frozen = freeze(ValueClass())

    assert type(frozen) is FrozenProxy
    assert type(frozen.set) is frozenset
    assert type(frozen.list) is tuple
    assert type(frozen.dict) is frozendict
    assert type(frozen.property_simple_value) is tuple
    assert type(frozen.method) is FrozenProxy
    assert type(frozen.inner) is FrozenProxy
    assert type(frozen.inner["key"]) is FrozenProxy
    assert type(frozen.inner.key.inner_key) is str
    assert type(frozen.property_inner_value) is FrozenProxy

    method_result = frozen.method([1, set()])
    assert method_result == (1, frozenset())
    assert type(method_result) is tuple
    assert type(method_result[1]) is frozenset


@pytest.mark.parametrize(
    "setter",
    [
        lambda o: setattr(o, "set", {1, 2, 3}),
        lambda o: setattr(o, "not_set", {1, 2, 3}),
        lambda o: delattr(o, "set"),
        lambda o: setattr(o.inner["key"], "foo", "value"),
        lambda o: setitem(o.inner, "key", "value"),
        lambda o: setitem(o.inner, "non existing key", "value"),
        lambda o: setattr(o.inner.key, "foo", "value"),
    ],
)
def test_frozen_proxy_setters_raises(setter):
    frozen = freeze(ValueClass())
    with pytest.raises(TypeError):
        setter(frozen)


@pytest.mark.parametrize(
    "setter",
    [
        lambda o: setattr(o, "set", {1, 2, 3}),
        lambda o: setattr(o, "not_set", {1, 2, 3}),
        lambda o: delattr(o, "set"),
        lambda o: setattr(o.inner["key"], "foo", "value"),
        lambda o: setattr(o.inner.key, "foo", "value"),
    ],
)
def test_frozen_proxy_setting_the_same_value(setter):
    frozen = freeze(ValueClass())
    with pytest.raises(TypeError):
        setter(frozen)
