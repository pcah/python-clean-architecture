import pytest

from jsonweb import (
    decode,
    encode,
)

from pca.domain.policy import (
    Policy,
    policy_constructor,
)
from pca.utils.inspect import get_func_name


class FakeStrategyModule(object):
    """A class that mockups a module of strategies"""

    def a1(self):
        pass

    def a2(self):
        pass

    def b(self):
        pass


@decode.from_object(policy_constructor)
class SomePolicy(Policy):
    """
    A policy meant to test serialization features of Policy descendants.
    """

    SERIALIZED_ATTRS = ("test_attr",)
    STRATEGY_MODULE = FakeStrategyModule
    STRATEGY_CHOICES = {
        "role_a": (
            "a1",
            "a2",
        ),
        "role_b": ("b",),
    }

    def __init__(self, test_attr, **kwargs):
        self.test_attr = test_attr
        super(SomePolicy, self).__init__(**kwargs)


class TestPolicy(object):
    """Tests of Policy serialization feature."""

    policy_definition = {
        "test_attr": "test_attr_value",
        "role_a": "a1",
        "role_b": "b",
    }

    @pytest.fixture
    def policy(self):
        return SomePolicy(**self.policy_definition)

    def test_constructing_policy(self, policy):
        """Test that all attrs and strategies are actualy put into the policy"""
        for attr in SomePolicy.SERIALIZED_ATTRS:
            assert getattr(policy, attr) == self.policy_definition[attr]
        for role in SomePolicy.STRATEGY_CHOICES:
            strategy_name = get_func_name(getattr(policy, role))
            assert strategy_name == self.policy_definition[role]

    def test_decode_encode(self, policy):
        """Test that encoding/decoding save all policy serializable features"""
        policy_repr = encode.dumper(policy)
        new_policy = decode.loader(policy_repr)
        assert policy == new_policy
