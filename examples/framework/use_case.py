# -*- coding: utf-8 -*-
from dataclasses import dataclass
import typing as t

from marshmallow import Schema

from pca.exceptions import ProcessError, ValidationError
from pca.utils.functools import reify

from .dependency_injection import Container


@dataclass
class UseCaseInterface:
    action: str
    schema: Schema


@dataclass
class UseCaseInput:
    data: t.Dict[str, t.Any]
    action: t.Optional[str]


@dataclass
class UseCaseResult:
    errors: t.Dict[str, ProcessError]
    data: t.Dict[str, t.Any]

    @property
    def success(self):
        return not self.errors


class UseCase:
    """
    This is core object of the application. Its methods represent
    application-specific actions that can be taken or queries to ask.
    """
    Input: t.ClassVar[UseCaseInput]
    container: Container

    @property
    def interfaces(self) -> t.List[UseCaseInterface]:
        raise NotImplementedError

    def action(self, input: UseCaseInput):
        if self.is_available(input):  # TODO ToCToU problem?
            action_method = getattr(self, input.action, 'action')
            action_method(input.data)
        else:
            raise ValueError(input)  # TODO library-specific error class to throw

    def execute(self, input: UseCaseInput) -> UseCaseResult:
        """Executes the operation defined by the use_case."""
        try:
            data_after_validation = self.validate(input)
        except ValidationError as e:
            return UseCaseResult(errors=e.errors, data={})
        result = self.action(data_after_validation)
        return UseCaseResult(errors={}, data=result)

    def is_available(self, input: UseCaseInput):
        raise NotImplementedError

    def action(self, data: t.Mapping):
        raise NotImplementedError


# noinspection PyAbstractClass
class SimpleUseCase(UseCase):
    schema_class: t.Optional[t.ClassVar[Schema]] = None

    def __init__(self, container: Container):
        self.container = container

    @reify
    def interfaces(self) -> t.List[UseCaseInterface]:
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
