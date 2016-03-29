# -*- coding: utf-8 -*-
from mock import Mock

from dharma.data.traits import undefined_value, Nature, Trait


def test_trait_class_listener_decorator(nature_class):
    "Tests if class listener added with `class_listener` decorator is called"
    class MyClass(nature_class):

        def __init__(self):
            self.mock = Mock()

        @nature_class.a_trait.class_listener
        def some_trait_activated(self, old_value, new_value):
            self.mock(self, old_value, new_value)

    instance = MyClass()
    instance.a_trait = 1
    instance.mock.assert_called_once_with(instance, undefined_value, 1)


def test_trait_class_listener_init():
    "Tests if class listener added with trait's __init__ arg is called"
    mock = Mock()

    def a_listener(instance, old_value, new_value):
        mock(instance, old_value, new_value)

    class ANature(Nature):
        a_trait = Trait(class_listeners=[a_listener])

    instance = ANature()
    instance.a_trait = 2
    mock.assert_called_once_with(instance, undefined_value, 2)


def test_trait_instance_listener(nature_instance_with_listener):
    instance = nature_instance_with_listener
    instance.a_trait = 3
    instance.mock.assert_called_once_with(instance, undefined_value, 3)


def test_trait_listener_not_notified_when_theres_no_change(
        nature_instance_with_listener):
    instance = nature_instance_with_listener
    instance.a_trait = 4
    instance.a_trait = 4
    instance.a_trait = "a new value"
    expected = [
        ((instance, undefined_value, 4),),
        ((instance, 4, "a new value"),)
    ]
    assert instance.mock.call_args_list == expected
