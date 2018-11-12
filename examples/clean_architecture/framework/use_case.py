# -*- coding: utf-8 -*-
from dataclasses import dataclass
import typing as t

from dharma.exceptions import DharmaConfigError
from marshmallow import Schema

from .dependency_injection import AbstractContainer
from .logic import LogicError


@dataclass
class UseCaseInterface:
    action: str
    schema: Schema


@dataclass
class UseCaseInput:
    data: t.Dict[str, t.Any]
    action: str


@dataclass
class UseCaseResult:
    errors: t.Dict[str, LogicError]
    data: t.Dict[str, t.Any]

    @property
    def success(self):
        return not self.errors


class UseCase:
    """
    This is core object of the application. Its methods represent
    application-specific actions that can be taken or queries to ask.
    """
    input_class: t.ClassVar[UseCaseInput] = UseCaseInterface
    container: AbstractContainer

    @property  # reify
    def interface(self):
        raise NotImplementedError


class SimpleUseCase(UseCase):
    action: t.ClassVar[str]
    schema_class: t.Optional[t.ClassVar[Schema]] = None

    def __init__(self, container: AbstractContainer):
        if not self.action:
            raise DharmaConfigError(code='NO-USE-CASE-ACTION-SPECIFIED')
        self.container = container

    @property  # reify
    def interface(self):
        return UseCaseInterface(schema=self.schema_class, action=self.action)

    def execute(self, input: UseCaseInput) -> UseCaseResult:
        """Executes the operation defined by the use_case."""
        raise NotImplementedError

    def can_execute(self, input: UseCaseInput) -> UseCaseResult:
        """
        Check whether the operation defined by the use_case can be executed.

        Success with empty data by default.
        """
        return UseCaseResult(errors={}, data={})
