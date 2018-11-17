# -*- coding: utf-8 -*-
from dataclasses import dataclass
import typing as t

from marshmallow import Schema

from pca.utils.functools import reify

from .dependency_injection import AbstractContainer
from .logic import UseCaseError, ValidationError


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
    errors: t.Dict[str, UseCaseError]
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

    @reify
    def interface(self):
        raise NotImplementedError


# noinspection PyAbstractClass
class SimpleUseCase(UseCase):
    schema_class: t.Optional[t.ClassVar[Schema]] = None

    def __init__(self, container: AbstractContainer):
        self.container = container

    @reify
    def interfaces(self):
        return [UseCaseInterface(schema=self.schema_class, action='action')]

    def validate(self, input: UseCaseInput):
        context = self.get_context()
        schema = self.schema_class(context=context)
        return schema.load(input)

    def execute(self, input: UseCaseInput) -> UseCaseResult:
        """Executes the operation defined by the use_case."""
        try:
            dto = self.validate(input)
        except ValidationError as e:
            return UseCaseResult(errors=e.errors, data={})
        result = self.action(dto)
        return UseCaseResult(errors={}, data=result)

    def can_execute(self, input: UseCaseInput) -> UseCaseResult:
        """
        Check whether the operation defined by the use_case can be executed.

        Success with empty data by default.
        """
        try:
            self.validate(input)
        except ValidationError as e:
            return UseCaseResult(errors=e.errors, data={})
        return UseCaseResult(errors={}, data={})

    def get_context(self) -> dict:
        raise NotImplementedError

    def action(self, input) -> dict:
        raise NotImplementedError
