# -*- coding: utf-8 -*-
from unittest import mock

import pytest

from dharma.utils import serialization


def test_load_simple():
    contents = (
        "---\n"
        "1: 2\n"
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


@pytest.mark.parametrize("file_extension, file_contents, expected_contents", [
    ('yaml', (
        "---\n"
        "- spam\n"
        "- eggs\n"
    ), ['spam', 'eggs']),
    ('json', '["spam", "eggs"]', ['spam', 'eggs']),
    ('JSON', '["spam", "eggs"]', ['spam', 'eggs']),
    ('txt', "['spam', 'eggs']", "['spam', 'eggs']"),
])
def test_load_with_include(file_extension, file_contents, expected_contents):
    main_contents = (
        "---\n"
        "foo: bar\n"
        "included: !include inner.{}".format(file_extension)
    )

    with mock.patch('dharma.utils.serialization._read_from_file') as mocked_read_from_file:
        mocked_read_from_file.return_value = file_contents
        result = serialization.load(main_contents)

    assert result == {
        'foo': 'bar',
        'included': expected_contents,
    }
