import typing as t

from .dao import IDao
from .entity import Entity, Id


class IRepository(t.Generic[Id, Entity]):
    """
    Repository serves as a collection of entites (with methods such as get, add, update, remove)
    with underlying persistence layer. Should know how to construct an instance, serialize it
    and get its id.

    Developers of repos for concrete entites are encouraged to subclass and put a meaningful
    query and command methods along the basic ones.
    """
    dao: t.ClassVar[IDao]
    """
    Data Access Object which gives repo a persistence API. Its value is created
    by requiring the DAO instance related to its entity from DI container.
    """
    entity: t.ClassVar[t.Type[Entity]]
    """Entity type collected by this repo."""

    def create(self, **kwargs) -> Entity:
        """
        Creates an object compatible with this repo. Uses repo's factory
        or the klass iff factory not present.

        NB: Does not inserts the object to the repo. Use `create_and_add` method for that.
        """

    def add(self, entity: Entity):
        """Adds the object to the repo to the underlying persistence layer via its DAO."""

    def create_and_add(self, **kwargs) -> Entity:
        """Creates an object compatible with this repo and adds it to the collection."""

    def find(self, id_: Id) -> t.Optional[Entity]:
        """Returns object of given id or None"""

    def contains(self, id_: Id):
        """Checks whether an entity of given id is in the repo."""

    def update(self, entity: Entity) -> None:
        """Updates the object in the repo."""

    def remove(self, entity: Entity) -> None:
        """Removes the object from the underlying persistence layer via DAO."""
