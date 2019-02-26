# -*- coding: utf-8 -*-
import mock

import pytest

from pca.utils.functools import error_catcher, reify


class TestReify:

    @pytest.fixture
    def reified(self):
        def wrapped(instance):
            return 'a'

        return reify(wrapped)

    @pytest.fixture
    def instance(self):
        class Dummy(object):

            mock = mock.MagicMock()

            @reify
            def b(self):
                self.mock(self)
                return object()

        return Dummy()

    def test___get__with_inst(self, reified, instance):
        result = reified.__get__(instance)
        assert result == 'a'
        assert instance.__dict__['wrapped'] == 'a'

    def test___get__wo_inst(self, reified):
        result = reified.__get__(None)
        assert result == reified

    def test_cache_value(self, instance):
        result_1 = instance.b
        result_2 = instance.b
        assert result_1 is result_2
        instance.mock.assert_called_once_with(instance)


class MyError(Exception):
    pass


class TestErrorCatcher:

    @pytest.fixture
    def function(self):
        m = mock.Mock(return_value=42)
        m.__qualname__ = 'a_function'
        m.__module__ = 'a_module'
        return m

    @pytest.fixture
    def error(self):
        return MyError('specific_error')

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

        with pytest.raises(MyError):
            decorated(1, foo='bar')
        error_function.assert_called_once_with(1, foo='bar')

    def test_error_multiple_error_class(self, error_function):
        decorated = error_catcher(error_class=(ValueError, MyError))(error_function)

        decorated(1, foo='bar')
        error_function.assert_called_once_with(1, foo='bar')
