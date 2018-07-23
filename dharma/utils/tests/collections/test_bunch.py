# -*- coding: utf-8 -*-
import pytest

from dharma.utils.collections import Bunch


@pytest.fixture
def bunch():
    return Bunch()


@pytest.fixture
def bunch_foo():
    return Bunch(foo='bar')


def test_getattr(bunch_foo):
    assert bunch_foo.foo == 'bar'
    with pytest.raises(AttributeError):
        # noinspection PyStatementEffect
        bunch_foo.bar


def test_getitem(bunch_foo):
    assert bunch_foo['foo'] == 'bar'
    with pytest.raises(KeyError):
        # noinspection PyStatementEffect
        bunch_foo['bar']


def test_setattr(bunch):
    bunch.foo = 'bar'
    assert bunch['foo'] == 'bar'


def test_setitem(bunch):
    bunch['foo'] = 'bar'
    assert bunch.foo == 'bar'


def test_delattr(bunch_foo):
    del bunch_foo.foo
    assert 'foo' not in bunch_foo
    with pytest.raises(AttributeError):
        del bunch_foo.bar


def test_delitem(bunch_foo):
    del bunch_foo['foo']
    assert 'foo' not in bunch_foo
    with pytest.raises(KeyError):
        del bunch_foo['bar']


def test_get_old(bunch_foo):
    assert bunch_foo.get('foo') == 'bar'
    assert bunch_foo.get('bar') is None
    assert bunch_foo.get('bar', 42) == 42


def test_get_dict(bunch):
    bunch['foo'] = {'bar': 'baz'}
    assert bunch.get('foo.bar') == 'baz'
    assert bunch.get('foo.foo') is None
    assert bunch.get('foo.bar.baz', 42) == 42


def test_get_list(bunch):
    bunch['foo'] = ['bar', {'baz': 1}]
    assert bunch.get('foo.0') == 'bar'
    assert bunch.get('foo.1.baz') == 1
    assert bunch.get('foo.2') is None
    assert bunch.get('foo.bar.baz', 42) == 42


def test_repr(bunch_foo):
    assert bunch_foo == eval(repr(bunch_foo))
