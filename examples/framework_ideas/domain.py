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
