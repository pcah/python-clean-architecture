import abc
import dataclasses


class ValueObject(abc.ABC):
    def __init_subclass__(cls, **kwargs):
        return dataclasses.dataclass(cls, init=True, frozen=True, repr=False)

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        """
        Repr respects only fields which values are not default
        (practical decision for large dataclasses).
        """
        # noinspection PyDataclass
        fields = ((f.name, getattr(self, f.name), f.default) for f in dataclasses.fields(self))
        fields_str = ", ".join(
            f"{name}={repr(value)}" for name, value, default in fields if value is not default
        )
        return f"{self.__class__.__qualname__}({fields_str})"
