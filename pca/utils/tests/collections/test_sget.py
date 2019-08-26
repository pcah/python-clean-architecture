import pytest

from pca.utils.collections import sget


class AClass:
    attribute = {'foo': 'bar'}

    @property
    def sub_attribute(self):
        return AClass()


sentinel = AClass()
dict_target = {
    'first_level': 'value',
    'second': {
        'level': 'value',
        'list': [{}, {'foo': 'list value'}],
        'non-list': {'1': {'foo': 'dict value'}},
    },
    1: 'int key',
    '1': 'string key',
    None: True,
    sentinel: 'sentinel value',
}


@pytest.mark.parametrize('key, result', [
    ('first_level', 'value'),
    (1, 'int key'),
    ('1', 'string key'),
    (None, True),
    (sentinel, 'sentinel value')
])
def test_simple_key(key, result):
    assert sget(dict_target, key) == result


@pytest.mark.parametrize('key, result', [
    ('second.level', 'value'),
    ('second.list.1.foo', 'list value'),
    ('second.non-list.1.foo', 'dict value'),
])
def test_key_structure(key, result):
    assert sget(dict_target, key) == result


@pytest.mark.parametrize('key, default, result', [
    ('second.level', 'not used', 'value'),
    ('second.non-existing', None, None),
    ('second.list.1.bar', 42, 42),
    ('second.non-list.17.foo', 42, 42),
])
def test_defaults(key, result, default):
    assert sget(dict_target, key, default) == result


def test_list_default():
    assert sget([1, 2, 3], '17', 'default') == 'default'


@pytest.mark.parametrize('key, default, result', [
    ('attribute', None, {'foo': 'bar'}),
    ('sub_attribute.attribute.foo', None, 'bar'),
    ('attribute.foo', None, 'bar'),
    ('attribute.baz', None, None),
    ('attribute.baz', 42, 42),
])
def test_attribute(key, default, result):
    assert sget(sentinel, key, default) == result
