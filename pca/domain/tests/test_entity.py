import dataclasses

import mock
import pytest

from pca.domain.entity import (
    AutoId,
    Entity,
    NaturalId,
    SequenceId,
    Uuid4Id,
)


@pytest.fixture(scope='session')
def data():
    return {'frame_type': 'gravel', 'wheel_type': 'road'}


def entity_constructor(id_field=None):
    id_field = id_field or SequenceId()

    class Bike(Entity):
        id = id_field
        frame_type: str
        wheel_type: str

    return Bike


class TestEntity:

    def test_identity(self, data):
        Bike = entity_constructor()
        entities = [Bike(**data).__set_id__(i) for i in range(4)]
        id_field = Bike.__get_id_field__()

        assert [e.__get_id__() for e in entities] == [0, 1, 2, 3]
        assert id_field.name == 'id'
        assert id_field.owner == Bike

    def test_no_identity(self):
        def entity_constructor():
            class EntityWithoutId(Entity):
                pass
            return EntityWithoutId

        with pytest.raises(AssertionError):
            entity_constructor()

    def test_too_many_identities(self):
        def entity_constructor():
            class EntityWith2Ids(Entity):
                id1 = SequenceId()
                id2 = Uuid4Id()
            return EntityWith2Ids

        with pytest.raises(AssertionError):
            entity_constructor()

    def test_inherited_id(self):
        Bike = entity_constructor()

        class Trike(Bike):
            index = NaturalId('frame_type', 'wheel_type')

        assert Trike.__get_id_field__() == Bike.id

    def test_overriding_inherited_id(self):
        Bike = entity_constructor()

        class Trike(Bike):
            __id_field_name__ = 'index'
            index = NaturalId('frame_type', 'wheel_type')

        assert Trike.__get_id_field__() == Trike.index

    def test_equality(self, data):
        Bike = entity_constructor()
        entity_1 = Bike(**data).__set_id__(1)
        entity_2 = Bike(**data).__set_id__(2)

        assert entity_1 != data
        assert entity_1 != entity_2

        entity_2.__set_id__(1)
        assert entity_1 == entity_2

    def test_serialization(self, data):
        Bike = entity_constructor()
        entity = Bike(**data).__set_id__(1)
        assert dataclasses.asdict(entity) == data


class TestAutoId:

    def test_value_generation(self, data):
        id_value = 42
        Bike = entity_constructor(AutoId(generator=lambda: id_value))
        entity = Bike(**data).__set_id__()
        assert entity.__get_id__() == id_value

        # when explicitly set, ID is the value you set
        entity.__set_id__(7)
        assert entity.__get_id__() == 7

        entity = Bike(**data).__set_id__()
        assert entity.__get_id__() == id_value


class TestSequenceId:

    def test_value_generation(self, data):
        Bike = entity_constructor()
        entity = Bike(**data).__set_id__()
        assert entity.__get_id__() == 1

        # new __set_id__ call to existing entity will generate a new ID,
        # which behaves as pseudo-cloning (mutability of the values might)
        entity.__set_id__()
        assert entity.__get_id__() == 2

        entity = Bike(**data).__set_id__()
        assert entity.__get_id__() == 3


class TestNaturalId:

    def test_value_generation(self, data):
        Bike = entity_constructor(NaturalId('frame_type', 'wheel_type'))
        entity = Bike(**data).__set_id__()
        assert entity.__get_id__() == ('gravel', 'road')

        # NaturalId ignores setting explicit value, it always gets it from
        # the values of natural key's fields
        entity.__set_id__(2)
        assert entity.__get_id__() == ('gravel', 'road')

        entity = Bike(1, 2).__set_id__(3)
        assert entity.__get_id__() == (1, 2)


class TestUuid4Id:

    @mock.patch('pca.domain.entity.uuid4')
    def test_value_generation(self, mocked_uuid4: mock.Mock, data):
        id_value = 'foo-bar'
        mocked_uuid4.return_value = id_value
        Bike = entity_constructor(Uuid4Id())
        entity = Bike(**data).__set_id__()
        assert entity.__get_id__() == id_value

        id_value = 'other-value'
        entity.__set_id__(id_value)
        assert entity.__get_id__() == id_value
