from configparser import ConfigParser
import pathlib  # noqa: F401
import typing as t


def load_ini_from_filepath(filepath: t.Union[str, 'pathlib.Path']) -> dict:
    config = ConfigParser()
    config.read(filepath)
    return {name: dict(section) for name, section in config.items()}
