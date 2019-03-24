import mock
import pytest

from pca.exceptions import ConfigError
from pca.utils.collections import frozendict
from pca.utils.dependency_injection import (
    Component,
    Container,
    DIErrors,
    container_supplier,
    inject,
    Inject,
    scope,
    Scopes,
)


class WheelInterface:
    name: str


class FrameInterface:
    name: str


@scope(Scopes.INSTANCE)
class RoadFrame(FrameInterface, Component):
    name = 'Road frame'


class GravelFrame(FrameInterface, Component):
    name = 'Gravel frame'


class CustomColoredFrame(FrameInterface, Component):
    def __init__(self, container, color):
        self.color = color
        super().__init__(container)

    @property
    def name(self):
        return f'Custom {self.color} frame'


class RoadWheel(WheelInterface, Component):
    name = 'Road wheel'


class GravelWheel(WheelInterface, Component):
    name = 'Gravel wheel'


class CustomColoredWheel(WheelInterface, Component):
    def __init__(self, container, color):
        self.color = color
        super().__init__(container)

    @property
    def name(self):
        return f'Custom {self.color} wheel'


class Bike:
    def __init__(self, container: Container):
        """
        Doesn't inherit Component features. Manually uses DI container as a dependency manager and
        sets injected instances to the Bike instance fields.
        """
        self.frame = container.find_by_name('frame')
        self.wheel = container.find_by_interface(WheelInterface)

    @property
    def components(self):
        return {
            'frame': self.frame.name,
            'wheel': self.wheel.name,
        }


class Trike(Component):
    """
    Inherits Component features. Automatically is being injected with DI instances using Inject
    descriptor.
    """
    front_wheel: WheelInterface = Inject()
    left_wheel = Inject(interface=WheelInterface)
    right_wheel = Inject(name='right')
    frame: FrameInterface = Inject(name='frame')

    @property
    def components(self):
        return {
            'front': self.front_wheel.name,
            'left': self.left_wheel.name,
            'right': self.right_wheel.name,
            'frame': self.frame.name,
        }


class TestContainer:
    def test_container_registration_(self, container):
        container.register_by_name(name='frame', constructor=RoadFrame)
        container.register_by_interface(interface=WheelInterface, constructor=RoadWheel)
        assert Bike(container).components == {
            'frame': 'Road frame',
            'wheel': 'Road wheel',
        }

    def test_container_interface_duplicates(self, container):
        interface = FrameInterface
        container.register_by_interface(interface, RoadFrame)
        # registering again the same signature results with an error
        with pytest.raises(ConfigError) as error_info:
            container.register_by_interface(interface, GravelFrame)
        assert error_info.value == DIErrors.AMBIGUOUS_DEFINITION
        assert error_info.value.params == {'identifier': interface, 'qualifier': None}
        # but registering with the same interface and different qualifier is a different signature
        # and ends with a success
        container.register_by_interface(interface, GravelFrame, qualifier='gravel')

    def test_container_interface_not_found(self, container):
        interface = FrameInterface
        qualifier = 'qualifier'
        with pytest.raises(ConfigError) as error_info:
            container.find_by_interface(interface, qualifier)
        assert error_info.value == DIErrors.DEFINITION_NOT_FOUND
        assert error_info.value.params == {'identifier': interface, 'qualifier': qualifier}

    def test_container_name_duplicates(self, container):
        name = 'frame'
        container.register_by_name(name=name, constructor=RoadFrame)
        # registering again the same signature results with an error
        with pytest.raises(ConfigError) as error_info:
            container.register_by_name(name=name, constructor=GravelFrame)
        assert error_info.value == DIErrors.AMBIGUOUS_DEFINITION
        assert error_info.value.params == {'identifier': name, 'qualifier': None}
        # but registering with the same interface and different qualifier is a different signature
        # and ends with a success
        container.register_by_name(name=name, constructor=GravelFrame, qualifier='gravel')

    def test_container_name_not_found(self, container):
        name = 'frame'
        qualifier = 'qualifier'
        with pytest.raises(ConfigError) as error_info:
            container.find_by_name(name, qualifier)
        assert error_info.value == DIErrors.DEFINITION_NOT_FOUND
        assert error_info.value.params == {'identifier': name, 'qualifier': qualifier}

    def test_constructor_kwargs(self, container):
        container.register_by_name(
            name='frame',
            constructor=CustomColoredFrame,
            kwargs={'color': 'pink'}
        )
        container.register_by_interface(
            interface=WheelInterface,
            constructor=CustomColoredWheel,
            kwargs={'color': 'pink'}
        )
        assert Bike(container).components == {
            'frame': 'Custom pink frame',
            'wheel': 'Custom pink wheel'
        }


class TestScopes:

    def test_scope_class(self, container):
        assert repr(Scopes.INSTANCE) == f'<Scopes.{Scopes.INSTANCE.name}>'
        assert Scopes.INSTANCE(container, RoadWheel, {}).name == 'Road wheel'

    def test_scope_decorator(self, container):
        @scope(Scopes.SINGLETON)
        class MyFrame(FrameInterface, Component):
            name = 'My frame'

        container.register_by_name(name='frame', constructor=MyFrame)
        instance_1 = container.find_by_name('frame')
        instance_2 = container.find_by_name('frame')
        assert MyFrame.__di_scope_type__ is Scopes.SINGLETON
        assert instance_1 is instance_2

    def test_singleton_scope(self, container):
        container.register_by_name(name='frame', constructor=RoadFrame, scope=Scopes.SINGLETON)
        instance_1 = container.find_by_name('frame')
        instance_2 = container.find_by_name('frame')
        assert instance_1 is instance_2


class TestInjectDescriptor:
    @pytest.fixture
    def container(self, container):
        container.register_by_interface(FrameInterface, RoadFrame)
        container.register_by_interface(WheelInterface, RoadWheel)
        container.register_by_name('frame', GravelFrame)
        container.register_by_name('wheels', RoadWheel)
        container.register_by_name('right', GravelWheel)

        return container

    def test_descriptor_injection(self, container):
        trike = Trike(container)
        assert trike.components == {
            'front': 'Road wheel',
            'left': 'Road wheel',
            'right': 'Gravel wheel',
            'frame': 'Gravel frame',
        }

    def test_get_class(self):
        class Bike(Component):
            wheel: WheelInterface = Inject()

        assert isinstance(Bike.wheel, Inject)

    def test_no_name_no_interface(self, container):
        class NoAnnotationBike(Component):
            wheel = Inject()

        with pytest.raises(ConfigError) as error_info:
            assert NoAnnotationBike(container).wheel
        assert error_info.value == DIErrors.NO_IDENTIFIER_SPECIFIED

    def test_dunder_dependencies(self, container):
        trike = Trike(container)
        assert isinstance(trike.__dependencies__, frozendict)
        assert trike.__dependencies__ == {
            'front_wheel': Trike.front_wheel,
            'left_wheel': Trike.left_wheel,
            'right_wheel': Trike.right_wheel,
            'frame': Trike.frame,
        }


class TestInjectDecorator:

    class Bike(Component):

        @inject
        def compose_success(
                self,
                frame: FrameInterface = Inject(),
                front_wheel=Inject(name='front'),
                rear_wheel=Inject(interface=WheelInterface)
        ):
            return {
                'frame': frame.name,
                'front': front_wheel.name,
                'rear': rear_wheel.name
            }

        @inject
        def compose_no_identifier(self, frame=Inject()):
            pass

    @pytest.fixture
    def container(self, container):
        container.register_by_interface(FrameInterface, RoadFrame)
        container.register_by_interface(WheelInterface, RoadWheel)
        container.register_by_name('front', GravelWheel)
        return container

    @pytest.fixture
    def instance(self, container):
        return self.Bike(container)

    def test_inject(self, instance):
        assert instance.compose_success() == {
            'frame': 'Road frame',
            'front': 'Gravel wheel',
            'rear': 'Road wheel',
        }

    def test_inject_args(self, container, instance):
        with pytest.raises(TypeError) as error_info:
            instance.compose_success(GravelFrame(container))
        assert str(error_info.value) == \
            "compose_success() got multiple values for argument 'frame'"

    def test_inject_kwargs(self, container, instance):
        assert instance.compose_success(frame=GravelFrame(container)) == {
            'frame': 'Gravel frame',
            'front': 'Gravel wheel',
            'rear': 'Road wheel',
        }

    def test_inject_no_name_or_interface(self, instance):
        with pytest.raises(ConfigError) as error_info:
            instance.compose_no_identifier()
        assert error_info.value == DIErrors.NO_IDENTIFIER_SPECIFIED

    def test_inject_no_container(self):
        # noinspection PyTypeChecker
        instance = self.Bike(None)
        with pytest.raises(ConfigError) as error_info:
            assert instance.compose_success()
        assert error_info.value == DIErrors.NO_CONTAINER_PROVIDED

    def test_injectable_function(self, container):
        mock_dependency = mock.Mock()
        container.register_by_name("dependency", lambda *args: mock_dependency)

        @container_supplier
        @inject
        def f(dependency=Inject(name="dependency"), **kwargs):
            # noinspection PyCallingNonCallable
            dependency(**kwargs)
            return 42

        f_closure = f(container)
        result = f_closure(foo='bar')

        mock_dependency.assert_called_once_with(foo='bar')
        assert result == 42
