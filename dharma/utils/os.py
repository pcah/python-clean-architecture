# -*- coding: utf-8 -*-
import pathlib


def read_from_file(filepath: str, encoding: str = None, errors: str = None):
    """Simple util meant to easy the process of mocking file opening"""
    return pathlib.Path(filepath).read_text(encoding=encoding, errors=errors)
