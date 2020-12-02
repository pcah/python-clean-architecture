import mock
import pytest

from pca.data.observable import Observable, undefined_value
from pca.utils.sentinel import Sentinel


@pytest.fixture
def owner():
    class Owner:
        observable = Observable()

    return Owner()


@pytest.fixture
def owner_with_instance_observer(owner):
    Owner = owner.__class__
    Owner.observer = mock.Mock()
    Owner.observable.add_instance_observer(owner, owner.observer)
    return owner


@pytest.fixture
def owner_with_validator():
    mock_validator = mock.Mock()

    class Owner:
        observable = Observable(validator=mock_validator)
        validator = mock_validator

    return Owner()


@pytest.fixture
def value():
    return Sentinel(name="value")


def test_default_sentinel(owner):
    assert owner.observable is undefined_value


def test_default_init(value):
    class Owner:
        observable = Observable(default=value)

    owner = Owner()
    assert owner.observable is value


def test_label(owner):
    assert owner.__class__.observable.label == "observable"
    with pytest.raises(AttributeError):
        owner.__class__.observable.label = "foo"


def test_class_observer_decorator(value):
    """Tests if class observer added with `class_observer` decorator is called"""

    class Owner:
        observable = Observable()
        observer = mock.Mock()

        @observable.class_observer
        def some_trait_activated(self, old_value, new_value):
            self.observer(self, old_value, new_value)

    instance = Owner()
    instance.observable = value
    instance.observer.assert_called_once_with(instance, undefined_value, value)


def test_class_observer_init(value):
    """Tests if class observer added with observable's __init__ arg is called"""
    observer = mock.Mock()

    class Owner:
        observable = Observable(class_observers=[observer])

    instance = Owner()
    instance.observable = value
    observer.assert_called_once_with(instance, undefined_value, value)


def test_instance_observer(owner_with_instance_observer):
    instance = owner_with_instance_observer
    instance.observable = value
    instance.observer.assert_called_once_with(instance, undefined_value, value)


def test_observer_not_notified_when_theres_no_change(owner_with_instance_observer):
    instance = owner_with_instance_observer
    value_1 = Sentinel("value_1")
    value_2 = Sentinel("value_2")
    instance.observable = value_1
    instance.observable = value_1
    instance.observable = value_2
    expected = [((instance, undefined_value, value_1),), ((instance, value_1, value_2),)]
    assert instance.observer.call_args_list == expected


def test_preprocessor(value):
    """Tests if preprocessor is used to prepare value of the trait"""
    preprocessor = mock.Mock(return_value=value)

    class Owner:
        observable = Observable(preprocessor=preprocessor)

    instance = Owner()

    pre_value = object()
    instance.observable = pre_value
    preprocessor.assert_called_once_with(pre_value)
    assert instance.observable is value


def test_validation_is_fired(owner_with_validator, value):
    """Tests if validators passed with `validator` argument are fired"""
    instance = owner_with_validator
    instance.observable = value
    instance.validator.assert_called_once_with(instance, undefined_value, value)


def test_validator_not_notified_when_theres_no_change(owner_with_validator):
    instance = owner_with_validator
    value_1 = Sentinel("value_1")
    value_2 = Sentinel("value_2")
    instance.observable = value_1
    instance.observable = value_1
    instance.observable = value_2
    expected = [((instance, undefined_value, value_1),), ((instance, value_1, value_2),)]
    assert instance.validator.call_args_list == expected


def test_del(owner):
    del owner.observable
    assert owner.observable is undefined_value
