import mock
import pytest

from pca.data.descriptors import (
    frozen,
    reify,
)


class TestReify:
    @pytest.fixture
    def reified(self):
        def wrapped(instance):
            return "a"

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
        assert result == "a"
        assert instance.__dict__["wrapped"] == "a"

    def test___get__wo_inst(self, reified):
        result = reified.__get__(None, None)
        assert result == reified

    def test_cache_value(self, instance):
        result_1 = instance.b
        result_2 = instance.b
        assert result_1 is result_2
        instance.mock.assert_called_once_with(instance)


# noinspection PyStatementEffect
class TestFrozen:
    class ValueClass:
        field: set = frozen()

    @pytest.fixture
    def instance(self):
        return self.ValueClass()

    def test_descriptor_access(self, instance):
        descriptor = instance.__class__.field
        assert type(descriptor) == frozen

    def test_value_not_set(self, instance):
        with pytest.raises(TypeError):
            instance.field

    @pytest.mark.parametrize(
        "value, frozen_value",
        [({1}, frozenset({1})), (frozenset({1}), frozenset({1})), (None, None),],
    )
    def test_raises_on_second_assignment(self, instance, value, frozen_value):
        instance.field = value
        assert instance.field == frozen_value
        with pytest.raises(TypeError):
            instance.field = set()

    @pytest.mark.parametrize(
        "value, second_value", [({1}, {1}), ({1}, frozenset({1})), (None, None),],
    )
    def test_not_raises_when_value_dont_change(self, instance, value, second_value):
        instance.field = value
        # second assignment doesn't mutate the value, should pass silently
        instance.field = second_value
