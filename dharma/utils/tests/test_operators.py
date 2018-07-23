# -*- coding: utf-8 -*-
import pytest

from dharma.exceptions import PathNotFoundError
from dharma.utils.operators import (
    eq,
    resolve_path,
    test_path as operator_test_path,  # avoids identifying as a test by pytest
)


@pytest.mark.parametrize('lhs, rhs', [
    ('foo', u'foo'),
    (u'foo', 'foo'),
    (u'foo', u'foo')
], ids=["rhs", "lhs", "both"])
def test_eq_unicode_warnings(lhs, rhs, recwarn):
    assert eq(lhs, rhs)
    assert not len(recwarn)


@pytest.mark.parametrize('path, expected', [
    (('foo',), 1),
    (('bar', 'baz'), {'a': 1}),
])
def test_resolve_path_dict_positive(example_dict, path, expected):
    resolve_path_curried = resolve_path(path)
    assert resolve_path_curried(example_dict) == expected


@pytest.mark.parametrize('path', [
    ('foo2',),
    ('foo2', 'bar'),
    ('foo', 'bar', 'baz', 'b'),
])
def test_resolve_path_dict_negative(example_dict, path):
    resolve_path_curried = resolve_path(path)
    with pytest.raises(PathNotFoundError):
        resolve_path_curried(example_dict)


@pytest.mark.parametrize('path, expected', [
    (('foo',), 1),
    (('bar', 'baz'), {'a': 1}),
])
def test_resolve_path_object_positive(example_object, path, expected):
    resolve_path_curried = resolve_path(path)
    assert resolve_path_curried(example_object) == expected


@pytest.mark.parametrize('path', [
    ('foo2',),
    ('foo2', 'bar'),
    ('foo', 'bar', 'baz', 'b'),
])
def test_resolve_path_object_negative(example_object, path):
    resolve_path_curried = resolve_path(path)
    with pytest.raises(PathNotFoundError):
        resolve_path_curried(example_object)


@pytest.mark.parametrize('path, expected', [
    (('foo',), True),
    (('bar', 'baz'), True),
    (('foo2',), False),
    (('foo2', 'bar'), False),
    (('foo', 'bar', 'baz', 'b'), False),
], ids=[
    "simple_positive",
    "complex_positive",
    "simple_negative",
    "complex_negative",
    "more_complex",
])
def test_test_path_dict(example_dict, path, expected):
    # this is the same as `bool`, but let's be explicite about intentions
    test = lambda lhs, value: bool(lhs)
    resolve_path_curried = operator_test_path(test, path)
    assert resolve_path_curried(example_dict) == expected


@pytest.mark.parametrize('path, expected', [
    (('foo',), True),
    (('bar', 'baz'), True),
    (('foo2',), False),
    (('foo2', 'bar'), False),
    (('foo', 'bar', 'baz', 'b'), False),
], ids=[
    "simple_positive",
    "complex_positive",
    "simple_negative",
    "complex_negative",
    "more_complex",
])
def test_test_path_object(example_object, path, expected):
    # this is the same as `bool`, but let's be explicit about intentions
    test = lambda lhs, value: bool(lhs)
    resolve_path_curried = operator_test_path(test, path)
    assert resolve_path_curried(example_object) == expected
