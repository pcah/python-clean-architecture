import pytest

from pca.utils.dependency_injection import (
    Container,
    Inject,
    scope,
    Scopes,
)


class WheelInterface:
    pass


class FrameInterface:
    pass


@scope(Scopes.INSTANCE)
class RoadFrame(FrameInterface):
    def __repr__(self):
        return f'<Road frame>'


class GravelFrame(FrameInterface):
    def __repr__(self):
        return f'<Gravel frame>'


class RoadWheel(WheelInterface):
    def __repr__(self):
        return f'<Road wheels>'


class GravelWheel(WheelInterface):
    def __repr__(self):
        return f'<Gravel wheel>'


class Bike:
    def __init__(self, container: Container):
        self.frame = container.find_by_name('frame')
        self.wheel = container.find_by_interface(WheelInterface)

    def build_bike(self):
        return f'Frame: {self.frame}\nWheels: {self.wheel}'


@pytest.fixture
def container():
    return Container(default_scope=Scopes.INSTANCE)


class TestContainer:
    def test_container_registration(self, container):
        container.register_by_name(name='frame', constructor=RoadFrame)
        container.register_by_interface(interface=WheelInterface, constructor=RoadWheel)
        assert Bike(container).build_bike() == (
            'Frame: <Road frame>\nWheels: <Road wheels>'
        )

    def test_container_interface_duplicates(self, container):
        interface = FrameInterface
        container.register_by_interface(interface, RoadFrame)
        with pytest.raises(ValueError) as e:
            container.register_by_interface(interface, GravelFrame)
        assert str(e.value) == f'Ambiguous interface: {interface}.'
        container.register_by_interface(interface, GravelFrame, qualifier='gravel')

    def test_container_name_duplicates(self, container):
        name = 'frame'
        container.register_by_name(name=name, constructor=RoadFrame)
        with pytest.raises(ValueError) as e:
            container.register_by_name(name=name, constructor=GravelFrame)
        assert str(e.value) == f'Ambiguous name: {name}.'
        container.register_by_name(name=name, constructor=GravelFrame, qualifier='gravel')

    def test_scope_class(self, container):
        assert repr(Scopes.INSTANCE) == f'<Scopes.{Scopes.INSTANCE.name}>'
        assert repr(Scopes.INSTANCE(container, RoadWheel)) == f'<Road wheels>'


class TestInject:
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
        assert road_bike.build_bike() == 'Frame: <Road frame>\nWheels: <Road wheels>'

    def test_get_class(self):
        class Bike:
            wheel: WheelInterface = Inject()

        assert isinstance(Bike.wheel, Inject)

    def test_no_name_no_interface(self, container):
        class NoAnnotationBike:
            wheel = Inject()

            def __init__(self, container: Container):
                self.container = container

        with pytest.raises(TypeError) as e:
            NoAnnotationBike(container).wheel
        assert str(e.value) == 'Missing name or interface for Inject.'

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
        assert another_bike.build_bike() == 'Wheels: <Road wheels>, <Road wheels>, <Gravel wheel>.'
