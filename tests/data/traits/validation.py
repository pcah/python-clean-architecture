# -*- coding: utf-8 -*-
from mock import Mock
import pytest

from dharma.utils.tests.factories import nature_class_factory


@pytest.fixture
def nature_instance_with_validator():
    mock = Mock()

    def validator(instance, new_value):
        mock(instance, new_value)

    nature_class = nature_class_factory(
        trait_name='a_trait', nature_name='ANature',
        kwargs={'validators': [validator]}
    )
    nature_class.mock = mock
    return nature_class()


def test_validation_is_fired(nature_instance_with_validator):
    instance = nature_instance_with_validator
    value = 'value to validate'
    instance.a_trait = value
    instance.mock.assert_called_once_with(instance, value)
