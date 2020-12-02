import typing as t
from dataclasses import asdict

from pca.data.errors import QueryErrors
from pca.interfaces.dao import Dto, IDao
from pca.interfaces.repository import Id, IRepository
from pca.data.descriptors import reify
from pca.utils.dependency_injection import Container

from .entity import Entity


class Factory:
    """
    A prototype serialization/validation class, designed to:
      * support dataclasses as entities
      * deconstruct specified fields (all dataclass fields by default)
    """

    # TODO #39 integrate with some kind of validation at the flow (application) layer
    # TODO #39 deconstruction of relations to other entites might consist of extraction their id
    # TODO #40 currently it doesn't care if values are entites.

    def __init__(self, entity: t.Type[Entity], fields: t.Collection[str] = None):
        self.entity = entity
        self.mapped_fields = fields

    def construct(self, dto: Dto) -> Entity:
        """
        Defines a way to construct (aka deserialize) an entity from data.
        Simple construction may just call class with data as kwargs. Complex cases may
        call another serializers to construct dependent types.
        """
        entity = self.entity(**dto)
        # supporting immutable entities
        entity.__get_id_field__().__set_id__(entity, dto.__id__)
        return entity

    def deconstruct(self, entity: Entity) -> Dto:
        """
        Defines a way to deconstruct (aka serialize) entity object into simple values.
        Simple deconstruction may just extract values from fields.
        Complex cases may need to use another factory to deconstruct objects of dependent types.
        """
        data = asdict(entity)
        if self.mapped_fields:
            data = {field: value for field, value in data.items() if field in self.mapped_fields}
        dto = Dto(data)
        dto.__id__ = entity.__get_id__()
        return dto


class Repository(IRepository[Id, Entity]):
    """
    Repository serves as a collection of entites (get, add, update, remove) with underlying
    persistence layer. Via its factory class, it knows how to construct an instance of the entity,
    serialize it and get its id.

    Developers of repos for concrete entites are encouraged to subclass and put a meaningful
    query and command methods along the basic ones.
    """

    factory: t.ClassVar[t.Optional[Factory]] = None

    def __init__(self, container: Container, factory: Factory = None):
        self.factory: Factory = factory or self.factory
        if not self.factory:  # pragma: no cover
            raise QueryErrors.NO_FACTORY_DEFINED
        self.container = container

    @reify
    def dao(self) -> IDao:
        """
        Data Access Object which gives repository a persistence API. Its value is created
        by requiring it from DI container in the context of the entity given for this repo.
        """
        return self.container.find_by_interface(interface=IDao, qualifier=self.entity)

    @reify
    def entity(self):
        """Proxy to entity class defined by the factory."""
        return self.factory.entity

    def create(self, **kwargs) -> Entity:
        """
        Creates an object compatible with this repo. Uses repo's factory
        or the klass iff factory not present.

        NB: Does not inserts the object to the repo. Use `create_and_add` method for that.
        """
        return self.factory.construct(Dto(kwargs))

    def add(self, entity: Entity) -> Id:
        """Adds the object to the repo to the underlying persistence layer via its DAO."""
        kwargs = self.factory.deconstruct(entity)
        return self.dao.insert(**kwargs)

    def create_and_add(self, **kwargs) -> Entity:
        """Creates an object compatible with this repo and adds it to the collection."""
        entity = self.create(**kwargs)
        id_ = self.add(entity)
        entity.__id__ = id_
        return entity

    def find(self, id_: Id) -> t.Optional[Entity]:
        """Returns object of given id or None."""
        dto = self.dao.get(id_)
        if not dto:
            raise QueryErrors.NOT_FOUND.with_params(id=id_, entity=self.entity)
        entity = self.factory.construct(dto)
        return entity

    def contains(self, id_: Id) -> bool:
        """Checks whether an entity of given id is in the repo."""
        return self.dao.filter_by(id_=id_).exists()

    def update(self, entity: Entity) -> None:
        """Updates the object in the repo."""
        # TODO TBDL which layer should filter only changed fields of the entity
        # TODO update = self.factory.diff(entity)
        update = self.factory.deconstruct(entity)
        self.dao.filter_by(id_=entity.__get_id__()).update(**update)

    def remove(self, entity: Entity) -> None:
        """Removes the object from the underlying persistence layer via DAO."""
        entity_id = entity.__get_id__()
        result = self.dao.filter_by(id_=entity_id).remove()
        if not result:  # entity hasn't been found in the DAO
            raise QueryErrors.NOT_FOUND.with_params(id=entity_id, entity=entity)
