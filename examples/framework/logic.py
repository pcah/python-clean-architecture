# -*- coding: utf-8 -*-
import typing as t

from pca.exceptions import DharmaError


class UseCaseError(DharmaError):
    """Widest class of errors raised by any SimpleUseCase"""
    DEFAULT_AREA = ''


class LogicError(UseCaseError):
    """"""
    DEFAULT_AREA = 'LOGIC'


class ValidationError(UseCaseError):

    errors: t.Dict[str, 'ValidationError']

    def __init__(self, errors=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = errors or {}
