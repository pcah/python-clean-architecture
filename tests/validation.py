# -*- coding: utf-8 -*-
import pytest

from dharma.data.traits import Int, Text
from dharma.data.exceptions import TraitValidationError
from dharma.utils import frozendict

from .factories import build_datasets


class PositiveValidation(object):

    data = {
        (Int,): [1],  # Int
        (Int, (42,)): [1],  # Int with default value
        (Int, (), frozendict(cast=True)): [1, 1.0]  # Int with casting
    }

    datasets = build_datasets(data)

    @pytest.mark.parametrize("entity, value", datasets)
    def test_positive_validation(self, entity, value):
        setattr(entity, 'trait', value)


class NegativeValidation(object):

    data = {
        (Int,): [1, 1.0],
        (Text,): ['a', u'unicode'],
    }

    datasets = build_datasets(data)

    @pytest.mark.parametrize("entity, value", datasets)
    def test_negative_validation(self, entity, value):
        with pytest.raises(TraitValidationError):
            setattr(entity, 'trait', value)
