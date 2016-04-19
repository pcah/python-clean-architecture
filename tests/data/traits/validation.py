# -*- coding: utf-8 -*-
from mock import Mock
# import pytest

from dharma.utils.tests.factories import nature_class_factory


def test_validation_is_fired():
    "Tests if validators passed with `validators` arguemnt are fired"
    mock = Mock()

    def validator(instance, new_value):
        mock(instance, new_value)

    nature_class = nature_class_factory(
        trait_name='a_trait', nature_name='ANature',
        kwargs={'validators': [validator]}
    )
    instance = nature_class()

    value = 'value to validate'
    instance.a_trait = value
    mock.assert_called_once_with(instance, value)


def test_construct_validators(mocker):
    "Tests if genus is used to build validators"
    genus = object()
    with mocker.patch('dharma.data.traits.base.construct_validators'):
        nature_class = nature_class_factory(
            trait_name='a_trait', nature_name='ANature',
            kwargs={'genus': genus}
        )
        from dharma.data.traits.base import construct_validators
        construct_validators.assert_called_once_with(genus)


def test_validators_from_genus(mocker):
    "Tests if validators, built with construct_validators, are fired"
    genus = object()
    validator_mock = mocker.MagicMock()
    with mocker.patch('dharma.data.traits.base.construct_validators',
                      return_value=[validator_mock]):
        nature_class = nature_class_factory(
            trait_name='a_trait', nature_name='ANature',
            kwargs={'genus': genus}
        )
        instance = nature_class()
        value = 'value to validate'
        instance.a_trait = value
        validator_mock.assert_called_once_with(instance, value)
