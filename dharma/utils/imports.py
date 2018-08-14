# -*- coding: utf-8 -*-
import os
import six
import sys
import typing as t
from importlib import import_module
from functools import lru_cache


def import_all_names(_file, _name):
    """
    Util for a tricky dynamic import of all names from all submodules.
    Use it in the __init__.py using following idiom:

        import_all_names(__file__, __name__)

    Supports __all__ attribute of the submodules.
    """
    path = os.path.dirname(os.path.abspath(_file))
    parent_module = sys.modules[_name]

    for py in [filename[:-3] for filename in os.listdir(path)
               if filename.endswith('.py') and filename != '__init__.py']:
        module = __import__('.'.join([_name, py]), fromlist=[py])
        module_names = getattr(module, '__all__', None) or dir(module)
        objects = dict(
            (name, getattr(module, name))
            for name in module_names
            if not name.startswith('_')
        )
        for name, obj in objects.items():
            if hasattr(parent_module, name) and \
               getattr(parent_module, name) is not obj:
                msg = (
                    "Function import_all_names hit upon conflicting "
                    "names. '{0}' is already imported to {1} module."
                ).format(name, module)
                import warnings
                warnings.warn(msg)
            setattr(parent_module, name, obj)


# noinspection PyUnboundLocalVariable
def import_dotted_path(dotted_path: str) -> t.Type:
    """
    Import a dotted module path and return the attribute/class designated by
    the last name in the path. Raise ImportError if the import failed.

    Code taken from: django.utils.module_loading,import_string v 1.9
    """
    try:
        module_path, qual_name = dotted_path.rsplit(':', 1) \
            if ':' in dotted_path else dotted_path.rsplit('.', 1)
    except ValueError as e:
        msg = "'%s' doesn't look like a module path" % dotted_path
        raise ImportError(msg) from e

    obj = import_module(module_path)

    try:
        for chunk in qual_name.split('.'):
            obj = getattr(obj, chunk)
    except AttributeError as e:
        msg = "Module '%s' does not define a '%s' attribute/class" % (
            module_path, qual_name)
        raise ImportError(msg) from e
    return obj


@lru_cache(maxsize=None)
def get_dotted_path(klass: t.Type) -> str:
    return klass.__qualname__ if klass.__module__ is None else \
        klass.__module__ + "." + klass.__qualname__
