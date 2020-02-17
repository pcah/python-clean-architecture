import abc
import mock
import pytest

from pca.utils import compat
from pca.utils.functools import (
    error_catcher,
    singledispatchmethod,
)


class TestErrorCatcher:
    class MyError(Exception):
        pass

    @pytest.fixture
    def function(self):
        m = mock.Mock(return_value=42)
        m.__qualname__ = 'a_function'
        m.__module__ = 'a_module'
        return m

    @pytest.fixture
    def error(self):
        return self.MyError('specific_error')

    @pytest.fixture
    def error_function(self, function, error):
        function.side_effect = error
        return function

    @pytest.fixture
    def constructor(self):
        return mock.Mock(return_value='42')

    def test_success_wo_constructor(self, function):
        decorated = error_catcher()(function)

        assert decorated(1, foo='bar') == 42
        function.assert_called_once_with(1, foo='bar')

    def test_success_with_constructor(self, function, constructor):
        decorated = error_catcher(success_constructor=constructor)(function)

        assert decorated(1, foo='bar') == '42'
        function.assert_called_once_with(1, foo='bar')
        constructor.assert_called_once_with(
            args=(1,),
            kwargs={'foo': 'bar'},
            function_name='a_module.a_function',
            result=42
        )

    def test_error_with_constructor(self, error_function, constructor, error):
        decorated = error_catcher(error_constructor=constructor)(error_function)

        assert decorated(1, foo='bar') == '42'
        error_function.assert_called_once_with(1, foo='bar')
        constructor.assert_called_once_with(
            args=(1,),
            kwargs={'foo': 'bar'},
            function_name='a_module.a_function',
            error=error
        )

    def test_error_wo_constructor(self, error_function, error):
        decorated = error_catcher()(error_function)

        assert decorated(1, foo='bar') == error
        error_function.assert_called_once_with(1, foo='bar')

    def test_error_narrowed_error_class_caught(self, error_function):
        decorated = error_catcher(error_class=ValueError)(error_function)

        with pytest.raises(self.MyError):
            decorated(1, foo='bar')
        error_function.assert_called_once_with(1, foo='bar')

    def test_error_multiple_error_class(self, error_function):
        decorated = error_catcher(error_class=(ValueError, self.MyError))(error_function)

        decorated(1, foo='bar')
        error_function.assert_called_once_with(1, foo='bar')


# noinspection PyDecorator,PyNestedDecorators
class TestSingleDispatchMethod:

    def test_method_register(self):
        class A:
            @singledispatchmethod
            def t(self, arg):
                self.arg = "base"

            @t.register(int)
            def _(self, arg):
                self.arg = "int"

            @t.register(str)
            def _(self, arg):
                self.arg = "str"

        a = A()

        a.t(0)
        assert a.arg == "int"
        aa = A()
        assert hasattr(aa, 'arg') is False
        a.t('')
        assert a.arg == "str"
        aa = A()
        assert hasattr(aa, 'arg') is False
        a.t(0.0)
        assert a.arg == "base"
        aa = A()
        assert hasattr(aa, 'arg') is False

    def test_staticmethod_register(self):
        # noinspection PyNestedDecorators
        class A:
            @singledispatchmethod
            @staticmethod
            def t(arg):
                return arg

            @t.register(int)
            @staticmethod
            def _(arg):
                return isinstance(arg, int)

            @t.register(str)
            @staticmethod
            def _(arg):
                return isinstance(arg, str)

        a = A()

        assert a
        assert A.t(0) is True
        assert A.t('') is True
        assert A.t(0.0) == 0.0

    def test_classmethod_register(self):
        # noinspection PyNestedDecorators
        class A:
            def __init__(self, arg):
                self.arg = arg

            @singledispatchmethod
            @classmethod
            def t(cls, arg):
                return cls("base")

            @t.register(int)
            @classmethod
            def _(cls, arg):
                return cls("int")

            @t.register(str)
            @classmethod
            def _(cls, arg):
                return cls("str")

        assert A.t(0).arg == "int"
        assert A.t('').arg == "str"
        assert A.t(0.0).arg == "base"

    def test_callable_register(self):
        # noinspection PyNestedDecorators
        class A:
            def __init__(self, arg):
                self.arg = arg

            @singledispatchmethod
            @classmethod
            def t(cls, arg):
                return cls("base")

        @A.t.register(int)
        @classmethod
        def _(cls, arg):
            return cls("int")

        @A.t.register(str)
        @classmethod
        def _(cls, arg):
            return cls("str")

        assert A.t(0).arg == "int"
        assert A.t('').arg == "str"
        assert A.t(0.0).arg == "base"

    def test_abstractmethod_register(self):
        class Abstract(abc.ABCMeta):

            @singledispatchmethod
            @abc.abstractmethod
            def add(self, x, y):
                pass

        assert Abstract.add.__isabstractmethod__ is True

    @pytest.mark.skipif(
        compat.PY36, reason="functools.singledispatch supports annotations since Py37")
    def test_type_annotation_register(self):
        class A:
            @singledispatchmethod
            def t(self, arg):
                return "base"

            @t.register
            def _(self, arg: int):
                return "int"

            @t.register
            def _(self, arg: str):
                return "str"

        a = A()

        assert a.t(0) == "int"
        assert a.t('') == "str"
        assert a.t(0.0) == "base"
