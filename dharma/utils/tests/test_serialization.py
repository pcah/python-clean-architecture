# -*- coding: utf-8 -*-
from unittest import mock

import pytest

from dharma.utils import serialization


def test_load_simple():
    contents = (
        "---\n"
        "1: 2\n"
        "# a comment\n"
        "foo: bar\n"
        "meal:\n"
        "  - spam\n"
        "  - spam\n"
        "  - eggs\n"
        "  - spam\n"
    )
    assert serialization.load(contents) == {
        1: 2,
        'foo': 'bar',
        'meal': ['spam', 'spam', 'eggs', 'spam']
    }


def test_load_dict_with_list_as_key():
    contents = (
        "---\n"
        "[1, 2]: this key has YAML list as a key; a tuple in Python\n"
    )
    assert serialization.load(contents) == {
        (1, 2): 'this key has YAML list as a key; a tuple in Python',
    }


@pytest.mark.parametrize("main_contents, inner_contents", [
    ((  # test include
        "---\n"
        "foo: [spam, eggs]\n"
        "included: !include inner.yaml"
    ), (
        "---\n"
        "bar:\n"
        "- spam\n"
        "- eggs\n"
    )),
    ((  # test include with anchors between inner & main files
        "---\n"
        "foo: &anchor [spam, eggs]\n"
        "included: !include inner.yaml"
     ), (
        "---\n"
        "bar: *anchor\n"
    )),
])
def test_load_with_include(main_contents, inner_contents):
    with mock.patch('dharma.utils.serialization.read_from_file') as mocked_read_from_file:
        mocked_read_from_file.return_value = inner_contents
        result = serialization.load(main_contents)

    assert result == {
        'foo': ['spam', 'eggs'],
        'included': {'bar': ['spam', 'eggs']},
    }


def test_load_from_file():
    contents = (
        "---\n"
        "foo: bar\n"
    )

    with mock.patch('dharma.utils.serialization.read_from_file') as mocked_read_from_file:
        mocked_read_from_file.return_value = contents
        result = serialization.load_from_filepath('path/to/a/file.yaml')

    assert result == {'foo': 'bar'}
    mocked_read_from_file.assert_called_with('path/to/a/file.yaml')


def test_construct_object():
    class FooClass(serialization.yaml.YAMLObject):
        yaml_tag = 'foo'
        yaml_constructor = serialization.CustomLoader

    contents = (
        "---\n"
        "foo: !<foo> {}\n"
    )
    foo_object = serialization.load(contents)['foo']
    assert isinstance(foo_object, FooClass)


def test_construct_namedtuple():
    """Original Loader has a problem of building an object which state is set
    by __new__, instead of __init__.
    """
    from collections import namedtuple

    class FooClass(serialization.yaml.YAMLObject, namedtuple('Foo', "x, y")):
        yaml_tag = 'foo'
        yaml_constructor = serialization.CustomLoader

        def __setstate__(self, data):
            self.data = data

    contents = (
        "---\n"
        "foo: !<foo> {x: 1, y: 2}\n"
    )
    foo_object = serialization.load(contents)['foo']
    assert isinstance(foo_object, FooClass)
    assert foo_object.data == {'x': 1, 'y': 2}
