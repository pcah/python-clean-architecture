from enum import Enum
from functools import partial
from pathlib import Path
import typing as t

from .ini import load_ini_from_filepath
from .json import load_json_from_filepath
from .yaml import load_yaml_from_filepath


def load_from_filepath(filepath: t.Union[str, Path]) -> t.Any:
    path = Path(filepath)
    loader = Loaders.guess_loader(path)
    return loader(path)


Loader = t.Callable[[Path], t.Any]


class Loaders(Enum):
    ini: Loader = partial(load_ini_from_filepath)
    json: Loader = partial(load_json_from_filepath)
    # TODO json_lines
    yaml: Loader = partial(load_yaml_from_filepath)

    @classmethod
    def __extension_map__(cls) -> dict:
        return {
            ".ini": cls.ini,
            ".cfg": cls.ini,
            ".json": cls.json,
            ".js": cls.json,
            ".yaml": cls.yaml,
            ".yml": cls.yaml,
        }

    @classmethod
    def guess_loader(cls, filepath: Path) -> t.Optional[t.Callable[[Path], t.Any]]:
        extension = filepath.suffix.lower()
        return cls.__extension_map__().get(extension)

    def __call__(self, filepath: Path):
        return self.value(filepath)
