# -*- coding: utf-8 -*-
from unittest import mock

import pytest

from pca.utils.functools import reify


@pytest.fixture
def reified():
    def wrapped(instance):
        return 'a'

    return reify(wrapped)


@pytest.fixture
def instance():
    class Dummy(object):

        mock = mock.MagicMock()

        @reify
        def b(self):
            self.mock(self)
            return object()

    return Dummy()


def test___get__withinst(reified, instance):
    result = reified.__get__(instance)
    assert result == 'a'
    assert instance.__dict__['wrapped'] == 'a'


def test___get__noinst(reified):
    result = reified.__get__(None)
    assert result == reified


def test_cache_value(instance):
    result_1 = instance.b
    result_2 = instance.b
    assert result_1 is result_2
    instance.mock.assert_called_once_with(instance)
