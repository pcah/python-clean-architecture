from mock import Mock

from dharma.traits import Int, Nature

mock = Mock()


class MyClass(Nature):
    some_trait = Int()

    @some_trait.class_listener
    def some_trait_activated(self, old_value, new_value):
        # FIXME add trait to signature
        mock()


def test_trait_class_listener_decorator():
    "Tests if class listener added with `class_listener` decorator is called"
    instance = MyClass()
    instance.some_trait = 1
    mock.assert_called_once_with()
