# -*- coding: utf-8 -*-
from functools import lru_cache

from django.http.request import HttpRequest
from django.db import Model

from . import common


@lru_cache(maxsize=None)
def django_model_factory(entity: t.Type) -> Model:
    """Some implementation details."""


class DjangoDao(common.IDao):
    """Accepts django.db.Models to IDao interface"""

    def ___init___(self, container, qualifier):
        self.model = django_model_factory(qualifier)


class DjangoRequest(common.IRequest, HttpRequest):
    """TODO implement a IRequest facade here."""
    def __init__(self, container, qualifier):
        assert qualifier


class DjangoSessionStrategy:
    pass
