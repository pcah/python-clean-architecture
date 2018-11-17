# -*- coding: utf-8 -*-
from .file import FileRepository


metarepo = None
metarepo_filepath = None


def repository_constructor(**kwargs):
    pass


def get_metarepo():
    global metarepo
    if not metarepo:
        metarepo = FileRepository(klass=repository_constructor, filepath=metarepo_filepath)


def get_repo(class_path):
    return metarepo.get_by_id(class_path)
