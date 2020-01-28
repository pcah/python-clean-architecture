import dataclasses

# TODO #40. is entity module using dataclasses `field` or have its own API for `fields`?
# proxy import for now
field = dataclasses.field


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
        return dataclasses.dataclass(cls, eq=False)

    def __init__(self, **kwargs):
        """
        This initializer will be overridden by dataclass decorator above. It is needed to
        persuade static type checkers that Entities have initializers.
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


class Id:
    """
    Descriptor describing identity of an entity.
    """
    def __init__(self, *field_names):
        """
        Given field_names are fields of the owner to build an identity key.
        No `field_names` mean that id has to be auto-generated, not natural.
        """
        self._field_names = field_names

    def __set_name__(self, owner, name):
        assert not self._field_names or all(
            hasattr(owner.__annotations__, name)
            for name in self._field_names
        ), (
            f"Entity owner has to have all field_names as dataclass "
            f"annotations: {self._field_names}"
        )
        self._owner = owner
        self._name = name

    def __get__(self, instance, owner):
        if not instance:
            return self
        if not self._field_names:
            # TODO decide how to pass id auto-generation from
            # the implementation of the DAO to the Entity
            import random
            return random.randint(1, 1000000)
        return tuple(getattr(instance, v) for v in self._field_names)
