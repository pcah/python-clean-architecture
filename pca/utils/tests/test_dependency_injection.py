import mock
import pytest

from pca.exceptions import ConfigError
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
    pass


class FrameInterface:
    pass


@scope(Scopes.INSTANCE)
class RoadFrame(FrameInterface, Component):
    def __repr__(self):
        return '<Road frame>'


class GravelFrame(FrameInterface, Component):
    def __repr__(self):
        return '<Gravel frame>'


class CustomColoredFrame(FrameInterface, Component):
    def __init__(self, container, color):
        self.color = color
        super().__init__(container)

    def __repr__(self):
        return f'<Custom {self.color} frame>'


class RoadWheel(WheelInterface, Component):
    def __repr__(self):
        return '<Road wheel>'


class GravelWheel(WheelInterface, Component):
    def __repr__(self):
        return '<Gravel wheel>'


class CustomColoredWheel(WheelInterface):
    """
    We can, but we don't have to inherit from component, as long as we accept container
    as the first argument to the `__init__`.
    """

    def __init__(self, container, color):
        self.color = color

    def __repr__(self):
        return f'<Custom {self.color} wheel>'


class Bike:
    def __init__(self, container: Container, **kwargs):
        self.frame = container.find_by_name('frame')
        self.wheel = container.find_by_interface(WheelInterface)

    def build_bike(self):
        return f'Frame: {self.frame}\nWheels: {self.wheel}'


class TestContainer:
    def test_container_registration(self, container):
        container.register_by_name(name='frame', constructor=RoadFrame)
        container.register_by_interface(interface=WheelInterface, constructor=RoadWheel)
        assert Bike(container).build_bike() == (
            'Frame: <Road frame>\nWheels: <Road wheel>'
        )

    def test_container_interface_duplicates(self, container):
        interface = FrameInterface
        container.register_by_interface(interface, RoadFrame)
        with pytest.raises(ConfigError) as error_info:
            container.register_by_interface(interface, GravelFrame)
        assert error_info.value == DIErrors.AMBIGUOUS_DEFINITION
        assert error_info.value.params == {'identifier': interface, 'qualifier': None}
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
        with pytest.raises(ConfigError) as error_info:
            container.register_by_name(name=name, constructor=GravelFrame)
        assert error_info.value == DIErrors.AMBIGUOUS_DEFINITION
        assert error_info.value.params == {'identifier': name, 'qualifier': None}
        container.register_by_name(name=name, constructor=GravelFrame, qualifier='gravel')

    def test_container_name_not_found(self, container):
        name = 'frame'
        qualifier = 'qualifier'
        with pytest.raises(ConfigError) as error_info:
            container.find_by_name(name, qualifier)
        assert error_info.value == DIErrors.DEFINITION_NOT_FOUND
        assert error_info.value.params == {'identifier': name, 'qualifier': qualifier}

    def test_scope_class(self, container):
        assert repr(Scopes.INSTANCE) == f'<Scopes.{Scopes.INSTANCE.name}>'
        assert repr(Scopes.INSTANCE(container, RoadWheel, {})) == '<Road wheel>'

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
        assert Bike(container).build_bike() == (
            'Frame: <Custom pink frame>\nWheels: <Custom pink wheel>'
        )


class TestScopes:

    def test_scope_decorator(self, container):
        @scope(Scopes.SINGLETON)
        class MyFrame(FrameInterface, Component):
            def __repr__(self):
                return '<Road frame>'

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


class TestInjectParameters:
    @pytest.fixture
    def container(self, container):
        container.register_by_interface(FrameInterface, RoadFrame)
        container.register_by_name('wheels', RoadWheel)
        container.register_by_name('right', GravelWheel)
        container.register_by_interface(WheelInterface, RoadWheel)
        return container

    @pytest.fixture
    def road_bike(self, container):
        class RoadBike:
            frame: FrameInterface = Inject()
            wheel: WheelInterface = Inject(name='wheels')

            def __init__(self, container: Container):
                self.container = container

            def build_bike(self):
                return f'Frame: {self.frame}\nWheels: {self.wheel}'

        return RoadBike(container)

    def test_property_injection(self, road_bike):
        assert road_bike.build_bike() == 'Frame: <Road frame>\nWheels: <Road wheel>'

    def test_get_class(self):
        class Bike:
            wheel: WheelInterface = Inject()

        assert isinstance(Bike.wheel, Inject)

    def test_no_name_no_interface(self, container):
        class NoAnnotationBike:
            wheel = Inject()

            def __init__(self, container: Container):
                self.container = container

        with pytest.raises(ConfigError) as error_info:
            assert NoAnnotationBike(container).wheel
        assert error_info.value == DIErrors.NO_IDENTIFIER_SPECIFIED

    @pytest.fixture
    def another_bike(self, container):
        class AnotherBike:
            front_wheel: WheelInterface = Inject()
            left_wheel = Inject(interface=WheelInterface)
            right_wheel = Inject(name='right')

            def __init__(self, container: Container):
                self.container = container

            def build_bike(self):
                return f'Wheels: {self.front_wheel}, {self.left_wheel}, {self.right_wheel}.'

        return AnotherBike(container)

    def test_injecting(self, another_bike):
        assert another_bike.build_bike() == 'Wheels: <Road wheel>, <Road wheel>, <Gravel wheel>.'


class TestInjectDecorator:
    @pytest.fixture
    def container(self, container):
        container.register_by_interface(FrameInterface, RoadFrame)
        container.register_by_interface(WheelInterface, RoadWheel)
        container.register_by_name('g_wheel', GravelWheel)
        return container

    @pytest.fixture
    def bike_obj(self, container):
        class NewBike(Component):

            @inject
            def build(
                    self,
                    frame: FrameInterface = Inject(),
                    wheel=Inject(name='g_wheel')
            ):
                return f'Frame: {frame}\nWheels: {wheel}'

            @inject
            def build_frame(self, frame=Inject()):
                pass

        return NewBike(container)

    def test_inject(self, bike_obj):
        assert bike_obj.build() == 'Frame: <Road frame>\nWheels: <Gravel wheel>'

    def test_inject_args(self, container, bike_obj):
        with pytest.raises(TypeError) as e:
            bike_obj.build(GravelFrame(container))
        assert str(e.value) == "build() got multiple values for argument 'frame'"

    def test_inject_kwargs(self, container, bike_obj):
        assert (
            bike_obj.build(frame=GravelFrame(container)) ==
            'Frame: <Gravel frame>\nWheels: <Gravel wheel>'
        )

    def test_inject_no_name_or_interface(self, bike_obj):
        with pytest.raises(ConfigError) as error_info:
            bike_obj.build_frame()
        assert error_info.value == DIErrors.NO_IDENTIFIER_SPECIFIED

    @pytest.fixture
    def no_container_bike_obj(self):
        class NewBike:
            @inject
            def build(self, frame: FrameInterface = Inject(), wheel: WheelInterface = Inject()):
                return f'Frame: {frame}\nWheels: {wheel}'

        return NewBike()

    def test_inject_no_container(self, no_container_bike_obj):
        with pytest.raises(ConfigError) as error_info:
            assert no_container_bike_obj.build()
        assert error_info.value == DIErrors.NO_CONTAINER_PROVIDED

    def test_injectable_function(self, container, ):
        mock_dependency = mock.Mock()
        container.register_by_name("dependency", lambda *args: mock_dependency)

        @container_supplier
        @inject
        def f(dependency=Inject(name="dependency"), **kwargs):
            dependency(**kwargs)
            return 42

        f_closure = f(container)
        result = f_closure(foo='bar')

        mock_dependency.assert_called_once_with(foo='bar')
        assert result == 42
