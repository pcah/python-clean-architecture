# -*- coding: utf-8 -*-
from mock import Mock
import pytest

from pca.utils.testing.factories import nature_class_factory


@pytest.fixture
def nature_class():
    return nature_class_factory(trait_name='a_trait', nature_name='ANature')


@pytest.fixture
def nature_instance(nature_class):
    return nature_class()


@pytest.fixture
def nature_instance_with_listener(nature_instance):
    nature_instance.mock = Mock()

    def a_listener(instance, old_value, new_value):
        instance.mock(instance, old_value, new_value)

    nature_instance.dharma['a_trait'].add_instance_listener(
        nature_instance, a_listener)
    return nature_instance


@pytest.fixture(scope='session')
def example_dict():
    return {
        'foo': 1,
        'bar': {
            'baz': {'a': 1},
        }
    }


@pytest.fixture(scope='session')
def example_object():

    class A(object):
        pass

    obj = A()
    bar = A()
    obj.foo = 1
    bar.baz = {'a': 1}
    obj.bar = bar
    return obj
