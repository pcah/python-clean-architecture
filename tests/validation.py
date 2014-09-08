from .factories import build_datasets

import pytest

from dharma.traits import Int, String
from dharma.exceptions import TraitValidationError
from dharma.utils import frozendict


class PositiveValidation(object):

    data = {
        (Int,): [1],  # Int
        (Int, (42,)): [1],  # Int with default value
        (Int, (), frozendict(cast=True)): [1, 1.0, 1L]  # Int with casting
    }

    datasets = build_datasets(data)

    @pytest.mark.parametrize("entity, value", datasets)
    def test_positive_validation(self, request):
        setattr(entity, 'trait', value)


class NegativeValidation(object):

    data = {
        (Int,): [1, 1.0, 1L],
        (String,): ['a', u'unicode'],
    }

    datasets = build_datasets(data)

    @pytest.mark.parametrize("entity, value", datasets)
    def test_negative_validation(self, entity, value):
        with pytest.raises(TraitValidationError):
            setattr(entity, 'trait', value)
