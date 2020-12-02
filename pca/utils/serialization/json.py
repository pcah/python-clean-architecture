import json
import pathlib  # noqa: F401
import typing as t

from pca.utils.os import read_from_file


def load_json_from_filepath(filepath: t.Union[str, "pathlib.Path"]) -> dict:
    contents = read_from_file(filepath)
    return json.loads(contents)
