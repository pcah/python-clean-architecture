# -*- coding: utf-8 -*-
import pytest

from dharma.utils.imports import import_dotted_path


class Foo:
    class Bar:
        def baz(self):
            """This is importable method"""
            return 42


def importable_function():
    pass


def test_import_dotted_class():
    result = import_dotted_path('imports.test_import_dotted_path.Foo')
    assert result is Foo


def test_import_dotted_function():
    result = import_dotted_path('imports.test_import_dotted_path.importable_function')
    assert result is importable_function


def test_import_colon_class():
    result = import_dotted_path('imports.test_import_dotted_path:Foo')
    assert result is Foo


def test_import_colon_inner_class():
    result = import_dotted_path('imports.test_import_dotted_path:Foo.Bar')
    assert result is Foo.Bar


def test_import_colon_inner_method():
    result = import_dotted_path('imports.test_import_dotted_path:Foo.Bar.baz')
    assert result is Foo.Bar.baz
    assert result(Foo.Bar()) == 42


def test_import_module_error():
    with pytest.raises(ImportError) as error_info:
        import_dotted_path('not_existing_module')
    assert error_info.value.msg == "'not_existing_module' doesn't look like a module path"


def test_import_attribute_error():
    with pytest.raises(ImportError) as error_info:
        import_dotted_path('imports.test_import_dotted_path:Bar')
    assert error_info.value.msg == (
        "Module 'imports.test_import_dotted_path' does not define a 'Bar' "
        "attribute/class"
    )
