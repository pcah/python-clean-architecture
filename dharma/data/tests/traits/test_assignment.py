# -*- coding: utf-8 -*-
from mock import Mock
import pytest

from dharma.exceptions import (
    TraitPreprocessorError,
    TraitValidationError,
)
from dharma.utils.testing.factories import nature_class_factory


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


def test_preprocessor_raises_generic_error():
    "Tests if assigning unpreprocessorable value raises TraitPreprocessorError"
    nature_class = nature_class_factory(
        trait_name='a_trait', nature_name='ANature',
        kwargs={'preprocessor': int}
    )
    instance = nature_class()

    value = 'value to preprocess'
    with pytest.raises(TraitPreprocessorError):
        instance.a_trait = value


def test_preprocessor_raises_validation_error():
    "Tests if assigning unpreprocessorable value raises TraitValidationError"
    mock = Mock(side_effect=TraitValidationError)

    nature_class = nature_class_factory(
        trait_name='a_trait', nature_name='ANature',
        kwargs={'preprocessor': mock}
    )
    instance = nature_class()

    value = 'value to preprocess'
    with pytest.raises(TraitValidationError):
        instance.a_trait = value
