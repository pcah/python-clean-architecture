# -*- coding: utf-8 -*-
from mock import Mock
import pytest

from dharma.data.exceptions import TraitRequiredError, TraitValidationError
from dharma.data.traits import undefined_value
from dharma.utils.tests.factories import nature_class_factory


@pytest.fixture
def nature_instance_with_validator():
    mock = Mock()

    def validator(instance, old_value, new_value):
        mock(instance, old_value, new_value)

    nature_class = nature_class_factory(
        trait_name='a_trait', nature_name='ANature',
        kwargs={'validators': [validator]}
    )
    instance = nature_class()
    instance.mock = mock
    return instance


def test_validation_is_fired(nature_instance_with_validator):
    "Tests if validators passed with `validators` arguemnt are fired"
    instance = nature_instance_with_validator
    new_value = 'value to validate'
    instance.a_trait = new_value
    instance.mock.assert_called_once_with(instance, undefined_value, new_value)


def test_construct_validators(mocker):
    "Tests if genus is used to build validators"
    genus = object()
    with mocker.patch('dharma.data.traits.trait.construct_validators'):
        nature_class_factory(
            trait_name='a_trait', nature_name='ANature',
            kwargs={'genus': genus}
        )
        from dharma.data.traits.trait import construct_validators
        construct_validators.assert_called_once_with(genus)


def test_validators_from_genus(mocker):
    "Tests if validators, built with construct_validators, are fired"
    genus = object()
    validator_mock = mocker.MagicMock()
    with mocker.patch('dharma.data.traits.trait.construct_validators',
                      return_value=[validator_mock]):
        nature_class = nature_class_factory(
            trait_name='a_trait', nature_name='ANature',
            kwargs={'genus': genus}
        )
        instance = nature_class()
        new_value = 'value to validate'
        instance.a_trait = new_value
        validator_mock.assert_called_once_with(
            instance, undefined_value, new_value)


def test_nature_validation_fires_trait_validators(
        nature_instance_with_validator):
    "Test if nature validation fires trait validators"
    instance = nature_instance_with_validator
    instance.dharma.validate(instance)
    instance.mock.assert_called_once_with(
        instance, undefined_value, undefined_value)


def test_nature_validation_checks_required_positive(
        nature_instance_with_validator):
    """Test if nature validation doesn't raise an TraitRequiredError while
    not required"""
    instance = nature_instance_with_validator
    instance.dharma['a_trait'].required = True
    instance.a_trait = 'a value'
    instance.dharma.validate(instance)


def test_nature_validation_checks_required_undefined(
        nature_instance_with_validator):
    "Test if nature validation raises an TraitRequiredError while undefined"
    instance = nature_instance_with_validator
    instance.dharma['a_trait'].required = True
    with pytest.raises(TraitValidationError) as e_info:
        instance.dharma.validate(instance)
    assert isinstance(e_info.value.errors['a_trait'], TraitRequiredError)


def test_nature_validation_checks_required_empty(
        nature_instance_with_validator):
    "Test if nature validation raises an TraitRequiredError while empty"
    instance = nature_instance_with_validator
    instance.dharma['a_trait'].required = True
    instance.a_trait = None
    with pytest.raises(TraitValidationError) as e_info:
        instance.dharma.validate(instance)
    assert isinstance(e_info.value.errors['a_trait'], TraitRequiredError)
