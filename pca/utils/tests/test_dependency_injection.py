import pytest

from pca.utils.dependency_injection import (
    Container,
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


class Bike:
    def __init__(self, container: Container):
        self.frame = container.find_by_name('frame')
        self.wheel = container.find_by_interface(WheelInterface)

    def build_bike(self):
        return f'Frame: {self.frame}\nWheels: {self.wheel}'


@pytest.fixture
def container():
    return Container(default_scope=Scopes.INSTANCE)


def test_container_registration(container):
    container.register_by_name(name='frame', constructor=RoadFrame)
    container.register_by_interface(interface=WheelInterface, constructor=RoadWheel)
    assert Bike(container).build_bike() == (
        'Frame: <Road frame>\nWheels: <Road wheels>'
    )


def test_container_interface_duplicates(container):
    interface = FrameInterface
    container.register_by_interface(interface, RoadFrame)
    with pytest.raises(ValueError) as e:
        container.register_by_interface(interface, GravelFrame)
    assert str(e.value) == f'Ambiguous interface: {interface}.'
    container.register_by_interface(interface, GravelFrame, qualifier='gravel')


def test_container_name_duplicates(container):
    name = 'frame'
    container.register_by_name(name=name, constructor=RoadFrame)
    with pytest.raises(ValueError) as e:
        container.register_by_name(name=name, constructor=GravelFrame)
    assert str(e.value) == f'Ambiguous name: {name}.'
    container.register_by_name(name=name, constructor=GravelFrame, qualifier='gravel')


def test_scope_class(container):
    assert repr(Scopes.INSTANCE) == f'<Scopes.{Scopes.INSTANCE.name}>'
    assert repr(Scopes.INSTANCE(container, RoadWheel)) == f'<Road wheels>'
