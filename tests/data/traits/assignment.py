# -*- coding: utf-8 -*-
from mock import Mock
# import pytest

from dharma.utils.tests.factories import nature_class_factory


def test_preprocessor():
    "Tests if preprocessor is used to prepare value of the trait"
    sentinel = object()
    preprocessor_mock = Mock(return_value=sentinel)

    nature_class = nature_class_factory(
        trait_name='a_trait', nature_name='ANature',
        kwargs={'preprocessor': preprocessor_mock}
    )
    instance = nature_class()

    value = 'value to preprocess'
    instance.a_trait = value
    preprocessor_mock.assert_called_once_with(value)
    assert instance.a_trait == sentinel
