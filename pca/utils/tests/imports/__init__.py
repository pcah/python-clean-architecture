# -*- coding: utf-8 -*-
# flake8: noqa
import pytest
import warnings

from pca.utils.imports import import_all_names


import_all_names(__file__, __name__)


def test_import():
    assert a
    assert Class
    assert function
    assert duplicated

    with pytest.raises(NameError):
        _private


def test_import_all():
    """Testing that import_all_names respects __all__ attribute of a module"""
    with pytest.raises(NameError):
        not_imported


def test_import_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        import_all_names(__file__, __name__)
        assert issubclass(w[-1].category, UserWarning)
        assert "conflicting names" in str(w[-1].message)
