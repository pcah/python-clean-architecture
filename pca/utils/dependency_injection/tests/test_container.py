import pytest

from pca.exceptions import ConfigError
from pca.utils.dependency_injection import (
    Container,
    Component,
    DIContext,
    DIErrors,
    Inject,
    Scopes,
    create_component,
    get_di_context,
    get_scope_type,
    scope,
)

from .components import (
    Bike,
    CustomColoredFrame,
    CustomColoredWheel,
    FrameInterface,
    GravelFrame,
    RoadFrame,
    RoadWheel,
    WheelInterface,
)


class TestContainer:
    def test_container_registration(self, container):
        container.register_by_name(name="frame", constructor=RoadFrame)
        container.register_by_interface(interface=WheelInterface, constructor=RoadWheel)
        assert Bike(container).components == {
            "frame": "Road frame",
            "wheel": "Road wheel",
        }

    def test_container_interface_duplicates(self, container):
        interface = FrameInterface
        container.register_by_interface(interface, RoadFrame)
        # registering again the same signature results with an error
        with pytest.raises(ConfigError) as error_info:
            container.register_by_interface(interface, GravelFrame)
        assert error_info.value == DIErrors.ALREADY_REGISTERED
        assert error_info.value.params == {"context": DIContext(interface=FrameInterface)}
        # but registering with the same interface and different qualifier is a different signature
        # and ends with a success
        container.register_by_interface(interface, GravelFrame, qualifier="gravel")

    def test_container_interface_not_found(self, container):
        interface = FrameInterface
        qualifier = "qualifier"
        with pytest.raises(ConfigError) as error_info:
            container.find_by_interface(interface, qualifier)
        assert error_info.value == DIErrors.DEFINITION_NOT_FOUND
        assert error_info.value.params == {
            "context": DIContext(interface=FrameInterface, qualifier="qualifier")
        }

    def test_container_name_duplicates(self, container):
        name = "frame"
        container.register_by_name(name=name, constructor=RoadFrame)
        # registering again the same signature results with an error
        with pytest.raises(ConfigError) as error_info:
            container.register_by_name(name=name, constructor=GravelFrame)
        assert error_info.value == DIErrors.ALREADY_REGISTERED
        assert error_info.value.params == {"context": DIContext(name="frame")}
        # but registering with the same interface and different qualifier is a different signature
        # and ends with a success
        container.register_by_name(name=name, constructor=GravelFrame, qualifier="gravel")

    def test_container_name_not_found(self, container):
        name = "frame"
        qualifier = "qualifier"
        with pytest.raises(ConfigError) as error_info:
            container.find_by_name(name, qualifier)
        assert error_info.value == DIErrors.DEFINITION_NOT_FOUND
        assert error_info.value.params == {
            "context": DIContext(name="frame", qualifier="qualifier")
        }

    def test_constructor_kwargs(self, container):
        container.register_by_name(
            name="frame", constructor=CustomColoredFrame, kwargs={"color": "pink"}
        )
        container.register_by_interface(
            interface=WheelInterface, constructor=CustomColoredWheel, kwargs={"color": "pink"}
        )
        assert Bike(container).components == {
            "frame": "Custom pink frame",
            "wheel": "Custom pink wheel",
        }


class TestScopes:
    def test_scope_class(self, container):
        assert repr(Scopes.INSTANCE) == f"<Scopes.{Scopes.INSTANCE.name}>"
        assert Scopes.INSTANCE(container, RoadWheel, {}).name == "Road wheel"

    def test_scope_decorator(self, container):
        @scope(Scopes.SINGLETON)
        class MyFrame(FrameInterface, Component):
            name = "My frame"

        container.register_by_name(name="frame", constructor=MyFrame)
        instance_1 = container.find_by_name("frame")
        instance_2 = container.find_by_name("frame")
        assert get_scope_type(MyFrame) is Scopes.SINGLETON
        assert instance_1 is instance_2

    def test_singleton_scope(self, container):
        container.register_by_name(name="frame", constructor=RoadFrame, scope=Scopes.SINGLETON)
        instance_1 = container.find_by_name("frame")
        instance_2 = container.find_by_name("frame")
        assert instance_1 is instance_2


class TestContext:
    @pytest.fixture
    def class_with_indeterminate_contexts(self, container):
        def get_qualifier(foo: "Foo") -> str:
            return foo.qualifier

        class Bar:
            pass

        class Foo(Component):
            qualifier = "qualifier"
            dependency = Bar

            bar = Inject(name="bar", get_qualifier=get_qualifier)
            baz = Inject(interface=Bar, get_qualifier=get_qualifier)

        container.register_by_name(
            name="bar",
            qualifier=Foo.qualifier,
            constructor=Bar,
        )
        container.register_by_interface(
            interface=Bar,
            qualifier=Foo.qualifier,
            constructor=Bar,
        )
        return Foo

    def test_get_di_context_by_name(self, container: Container):
        name = "frame"
        container.register_by_name(name=name, constructor=RoadFrame)
        instance = container.find_by_name(name)
        assert get_di_context(instance) == DIContext(name=name)

    def test_get_di_context_by_interface(self, container: Container):
        qualifier = "qualifier"
        container.register_by_interface(
            interface=WheelInterface, qualifier=qualifier, constructor=RoadWheel
        )
        instance = container.find_by_interface(WheelInterface, qualifier=qualifier)
        assert get_di_context(instance) == DIContext(interface=WheelInterface, qualifier=qualifier)

    def test_get_di_context_none(self):
        instance = object()
        assert get_di_context(instance) is None

    def test_empty_definition(self, container):
        with pytest.raises(ConfigError) as error_info:
            DIContext().get(container)
        assert error_info.value == DIErrors.NO_IDENTIFIER_SPECIFIED

    def test_ambiguous_definition(self, container):
        with pytest.raises(ConfigError) as error_info:
            DIContext(name="name", interface=str).get(container)
        assert error_info.value == DIErrors.AMBIGUOUS_DEFINITION
        assert error_info.value.params == dict(name="name", interface=str)

    def test_contradictory_qualifier_defined(self):
        get_qualifier = lambda target: "qualifier"
        with pytest.raises(ConfigError) as error_info:
            DIContext(name="name", qualifier="qualifier", get_qualifier=get_qualifier)
        assert error_info.value == DIErrors.CONTRADICTORY_QUALIFIER_DEFINED
        assert error_info.value.params == dict(qualifier="qualifier", get_qualifier=get_qualifier)

    def test_get_qualifier_on_class(self, class_with_indeterminate_contexts, container):
        context = class_with_indeterminate_contexts.bar.context
        # the Inject descriptor knows only about indeterminate DIContext with the `get_qualifier`
        # function
        assert context.get_qualifier.__name__ == "get_qualifier"
        assert not context.is_determined()

    def test_name_get_qualifier_on_instance(self, class_with_indeterminate_contexts, container):
        foo = create_component(class_with_indeterminate_contexts, container)
        bar_context = get_di_context(foo.bar)
        # the dependent on component has the dependency context already determined, based
        # on the dependant state
        assert bar_context == DIContext(
            name="bar", qualifier=class_with_indeterminate_contexts.qualifier
        )
        assert bar_context.is_determined()

    def test_interface_get_qualifier_on_instance(
        self, class_with_indeterminate_contexts, container
    ):
        foo = create_component(class_with_indeterminate_contexts, container)
        baz_context = get_di_context(foo.baz)
        # the dependent on component has the dependency context already determined, based
        # on the dependant state
        assert baz_context == DIContext(
            interface=class_with_indeterminate_contexts.dependency,
            qualifier=class_with_indeterminate_contexts.qualifier,
        )
        assert baz_context.is_determined()

    def test_indeterminate_context_being_resolved(self, container):
        get_qualifier = lambda target: "bar"
        context = DIContext(name="foo", get_qualifier=get_qualifier)
        with pytest.raises(ConfigError) as error_info:
            context.get(container)
        assert error_info.value == DIErrors.INDETERMINATE_CONTEXT_BEING_RESOLVED
        assert error_info.value.params == dict(
            name="foo", interface=None, get_qualifier=get_qualifier
        )
