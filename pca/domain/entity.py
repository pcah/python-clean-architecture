from dataclasses import dataclass

from pca.interfaces.entity import Id


class Entity:
    """
    Entity is a business logic pattern: it is thought to have a set of fields and methods
    that embody some knowledge about the domain.
    * Entity class is structured, which means that some relation to other entity is represented by
      concrete reference to the other object.
    * Entity (and an aggregate root especially) should represent complex data and shouldn't
      be normalized.
    """
    # TODO #40. should entities be frozen=True?

    __id__: Id = None

    def __init_subclass__(cls, **kwargs):
        return dataclass(cls, eq=False)

    def __init__(self, **kwargs):
        """
        This initializator will be overridden by dataclass decorator above. It is needed to
        persuade static type checkers that Entities have initializators.
        """

    @property
    def id(self) -> Id:
        """
        Defines access to the primary key of the object.
        NB: some of the DAOs will use some non-standard data type as primary key or a composite
        of values.
        """
        return self.__id__

    def __eq__(self, other) -> bool:
        """Entity is identified by the Id."""
        return isinstance(other, self.__class__) and other.id == self.id
