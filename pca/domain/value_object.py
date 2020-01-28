import abc
import dataclasses


class ValueObject(abc.ABC):
    def __init_subclass__(cls, **kwargs):
        return dataclasses.dataclass(cls, init=True, frozen=True, repr=False)

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        # noinspection PyDataclass
        fields = dataclasses.fields(self)
        fields_str = ', '.join(
            f"{f.name}={repr(value)}"
            for f in fields
            if (value := getattr(self, f.name)) is not f.default
        )
        return f"{self.__class__.__qualname__}({fields_str})"
