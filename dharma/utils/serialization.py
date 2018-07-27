# -*- coding: utf-8 -*-
import json
import os
import typing as t

from ruamel import yaml

from .os import read_from_file


class CustomLoader(yaml.Loader):
    """
    Custom YAML Loader with some extension features:
    * `!include` constructor which can incorporate another file (YAML, JSON or plain text lines)
    * supplies constructed object's arguments to __new__ during its construction (the old one
        forces __new__ without arguments)
    """
    def __init__(self, stream: t.IO, *args, **kwargs):
        """Find CWD as the root dir of the filepaths"""
        try:
            self.root = os.path.split(stream.name)[0]
        except AttributeError:
            self.root = os.path.curdir

        super().__init__(stream, *args, **kwargs)

    def construct_yaml_object(self, node: t.Any, cls: t.Any) -> t.Any:
        state = self.construct_mapping(node, deep=True)
        data = cls.__new__(cls, **state)
        if hasattr(data, '__setstate__'):
            data.__setstate__(state)
        yield data

    def fetch_comment(self, comment):
        raise NotImplementedError


def construct_include(loader: CustomLoader, node: yaml.Node) -> t.Any:
    """Include file referenced at node."""
    filepath = os.path.abspath(os.path.join(loader.root, loader.construct_scalar(node)))
    return load_from_filepath(filepath)


yaml.add_constructor('!include', construct_include, CustomLoader)


def load(stream: t.Union[str, t.IO]) -> t.Any:
    """
    Own YAML-deserialization based on:
        * ruamel.yaml (some additional bugfixes vs regular PyYaml module)
        * unsafe loading (be sure to use it only for own datafiles)
        * YAML inclusion feature
    """
    return yaml.load(stream, Loader=CustomLoader)


def load_from_filepath(filepath: t.Union[str, 'pathlib.Path']) -> t.Any:
    """
    See: `load` function. This function differs only with that it expects filepath as an argument.
    """
    extension = os.path.splitext(filepath)[1].lstrip('.').lower()
    contents = read_from_file(filepath)

    if extension in ('yaml', 'yml'):
        return load(contents)
    elif extension in ('json',):
        return json.loads(contents)
    else:
        return contents
