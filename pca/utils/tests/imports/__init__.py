# flake8: noqa
import pytest

from pca.utils.imports import import_all_names


with pytest.warns(UserWarning) as record:
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
    with pytest.warns(None) as record:
        import_all_names(__file__, __name__)
    assert issubclass(record[-1].category, UserWarning)
    assert "conflicting names" in str(record[-1].message)
