import dataclasses
import pytest

from pca.data.dao import IDao, InMemoryDao
from pca.data.errors import QueryErrors
from pca.domain.repository import Repository, Schema
from pca.domain.entity import Entity
from pca.exceptions import (
    ConfigError,
    QueryError,
)
from pca.interfaces.dao import Dto
from pca.utils.dependency_injection import Container, DIErrors


@dataclasses.dataclass
class Bike(Entity):
    frame_type: str
    wheel_type: str


@pytest.fixture(scope='session')
def data():
    return {'frame_type': 'gravel', 'wheel_type': 'road'}


@pytest.fixture(scope='session')
def schema():
    return Schema(Bike)


class TestSchema:

    @pytest.fixture
    def dto(self, data):
        dto = Dto(data)
        dto.__id__ = 17
        return dto

    @pytest.fixture
    def entity(self, dto):
        return Bike(**dto)

    def test_construction(self, dto):
        schema = Schema(Bike)
        entity = schema.construct(dto)
        assert isinstance(entity, Bike)
        assert entity.id == 17
        assert entity.frame_type == 'gravel'
        assert entity.wheel_type == 'road'

    def test_deconstruction(self, entity, data):
        schema = Schema(Bike)
        result = schema.deconstruct(entity)
        assert result == data
        assert result.id == entity.id

    def test_deconstruction_with_fields(self, entity, dto):
        schema = Schema(Bike, fields=('wheel_type',))
        result = schema.deconstruct(entity)
        assert result == {'wheel_type': 'road'}
        assert result.id == entity.id


class TestConstruction:

    @pytest.fixture
    def dao_class(self, container):
        container.register_by_interface(
            IDao, InMemoryDao,
            qualifier=Bike,
        )
        return InMemoryDao

    @pytest.fixture
    def repo(self, container, schema):
        return Repository(container, schema)

    def test_dao_injection_success(self, repo, dao_class):
        assert repo.entity is Bike
        assert isinstance(repo.dao, dao_class)

    def test_dao_injection_error(self, repo):
        assert repo.entity is Bike
        with pytest.raises(ConfigError) as error_info:
            assert repo.dao
        assert error_info.value == DIErrors.DEFINITION_NOT_FOUND
        assert error_info.value.params == {'identifier': IDao, 'qualifier': Bike}


class TestApi:

    @pytest.fixture
    def dao(self, container: Container):
        container.register_by_interface(
            IDao, InMemoryDao,
            qualifier=Bike,
        )
        return container.find_by_interface(IDao, qualifier=Bike)

    @pytest.fixture
    def repo(self, container, schema, dao):
        repo = Repository(container, schema)
        return repo

    def test_create(self, data, repo: Repository, dao: IDao):
        entity = repo.create(**data)
        assert repo.schema.deconstruct(entity) == data
        assert dao.all().count() == 0

    def test_add(self, data, repo: Repository, dao: IDao):
        entity = Bike(**data)
        id_ = repo.add(entity)
        assert dao.get(id_) == data

    def test_create_and_add(self, data, repo: Repository, dao: IDao):
        entity = repo.create_and_add(**data)
        assert dao.get(entity.id) == data

    def test_find_success(self, data, repo: Repository, dao: IDao):
        id_ = dao.insert(**data)
        entity = repo.find(id_)
        assert isinstance(entity, Bike)
        assert dataclasses.asdict(entity) == data

    def test_find_error(self, data, repo: Repository, dao: IDao):
        id_ = 42
        with pytest.raises(QueryError) as error_info:
            assert repo.find(id_)
        assert error_info.value == QueryErrors.NOT_FOUND
        assert error_info.value.params == {'id': id_, 'entity': Bike}

    def test_contains_success(self, data, repo: Repository, dao: IDao):
        id_ = dao.insert(**data)
        assert repo.contains(id_)

    def test_contains_failure(self, data, repo: Repository, dao: IDao):
        id_ = 42
        assert not repo.contains(id_)

    def test_update_success(self, data, repo: Repository, dao: IDao):
        id_ = dao.insert(**data)
        entity = repo.find(id_)
        entity.frame_type = 'road'
        repo.update(entity)
        assert dao.get(id_) == {'frame_type': 'road', 'wheel_type': 'road'}

    def test_remove_success(self, data, repo: Repository, dao: IDao):
        id_ = dao.insert(**data)
        entity = repo.find(id_)
        assert dao.filter_by(id_=id_).exists()
        repo.remove(entity)
        assert not dao.filter_by(id_=id_).exists()

    def test_remove_error_not_added(self, data, repo: Repository, dao: IDao):
        entity = repo.create(**data)
        with pytest.raises(QueryError) as error_info:
            repo.remove(entity)
        assert error_info.value == QueryErrors.ENTITY_NOT_YET_ADDED
        assert error_info.value.params == {'entity': entity}

    def test_remove_error_wrong_id(self, data, repo: Repository, dao: IDao):
        id_ = dao.insert(**data)
        entity = repo.find(id_)
        repo.remove(entity)
        with pytest.raises(QueryError) as error_info:
            repo.remove(entity)
        assert error_info.value == QueryErrors.NOT_FOUND
        assert error_info.value.params == {'id': id_, 'entity': entity}
