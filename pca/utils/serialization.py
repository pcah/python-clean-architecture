# -*- coding: utf-8 -*-
import os
import typing as t

from ruamel import yaml

from .os import read_from_file


class CustomLoader(yaml.Loader):
    """
    Custom YAML Loader with some extension features:
    * `!include` constructor which can incorporate another file (YAML, JSON or plain text lines)
    * its Composer class doesn't clear anchor aliases, so these may be used between (included)
        documents
    * supplies constructed object's arguments to __new__ during its construction (the old one
        forces __new__ without arguments
    """
    def __init__(self, stream: t.IO, *args, **kwargs):
        """Find CWD as the root dir of the filepaths"""
        try:
            self.root = os.path.split(stream.name)[0]
        except AttributeError:
            self.root = os.path.curdir

        super().__init__(stream, *args, **kwargs)

    def compose_document(self):
        """Look: https://stackoverflow.com/a/44913652"""
        self.parser.get_event()
        node = self.compose_node(None, None)
        self.parser.get_event()
        # self.anchors = {}  # clearing of anchors removed HERE
        return node

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
    return load_from_filepath(filepath, master=loader)


yaml.add_constructor('!include', construct_include, CustomLoader)


def load(
        stream: t.Union[str, t.IO],
        master: CustomLoader = None,
        version: str = None
) -> t.Any:
    """
    Own YAML-deserialization based on:
        * ruamel.yaml (some additional bugfixes vs regular PyYaml module)
        * unsafe loading (be sure to use it only for own datafiles)
        * YAML inclusion feature
    """
    loader = CustomLoader(stream, version=version)
    if master is not None:
        loader.anchors = master.anchors
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()
        try:
            loader._reader.reset_reader()
        except AttributeError:  # pragma: no cover
            pass
        try:
            loader._scanner.reset_scanner()
        except AttributeError:  # pragma: no cover
            pass


def load_from_filepath(
        filepath: t.Union[str, 'pathlib.Path'],
        master: CustomLoader = None
) -> t.Any:
    """
    See: `load` function. This function differs only with that it expects filepath as an argument.
    """
    contents = read_from_file(filepath)
    return load(contents, master=master)
