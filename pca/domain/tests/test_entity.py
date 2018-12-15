import pytest
import dataclasses

from pca.domain.entity import Entity


@pytest.fixture(scope='session')
def data():
    return {'frame_type': 'gravel', 'wheel_type': 'road'}


@dataclasses.dataclass(eq=False)
class Bike(Entity):
    frame_type: str
    wheel_type: str


def test_equality(data):
    entity_1 = Bike(**data)
    entity_1.__id__ = 1
    entity_2 = Bike(**data)
    entity_2.__id__ = 2

    assert entity_1 != data
    assert entity_1 != entity_2
    entity_2.__id__ = 1
    assert entity_1 == entity_2
