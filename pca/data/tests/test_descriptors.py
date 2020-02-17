import mock
import pytest

from pca.data.descriptors import (
    reify,
)


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
        result = reified.__get__(instance, instance)
        assert result == 'a'
        assert instance.__dict__['wrapped'] == 'a'

    def test___get__wo_inst(self, reified):
        result = reified.__get__(None, None)
        assert result == reified

    def test_cache_value(self, instance):
        result_1 = instance.b
        result_2 = instance.b
        assert result_1 is result_2
        instance.mock.assert_called_once_with(instance)
