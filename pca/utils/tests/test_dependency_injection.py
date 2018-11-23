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


class RoadWheel(WheelInterface):
    def __repr__(self):
        return f'<Road wheels>'


class Bike:
    def __init__(self, container: Container):
        self.frame = container.find_by_name('frame')
        self.wheel = container.find_by_name('wheel')

    def build_bike(self):
        return f"Frame: {self.frame}\nWheels: {self.wheel}"


@pytest.fixture
def container():
    return Container()


def test_container_registration(container):
    container.register_by_name(name='frame', constructor=RoadFrame)
    container.register_by_name(name='wheel', constructor=RoadWheel)
    assert Bike(container).build_bike() == (
        "Frame: <Road frame>\nWheels: <Road wheels>"
    )


def test_container_injection(container):
    name = 'frame'
    container.register_by_name(name=name, constructor=RoadFrame)
    with pytest.raises(ValueError) as e:
        container.register_by_name(name=name, constructor=RoadWheel)
    assert str(e.value) == f'Ambiguous name: {name}.'
