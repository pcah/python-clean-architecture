# -*- coding: utf-8 -*-
from dataclasses import dataclass
import typing as t

from .dependency_injection import AbstractContainer
from .logic import LogicError


@dataclass
class UseCaseInput:
    data: t.Dict[str, t.Any]
    action: t.Optional[str] = 'init'
    flow_id: t.Optional[str] = None
    state_id: t.Optional[str] = None


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
    container: AbstractContainer

    def __init__(self, container: AbstractContainer):
        self.container = container

    def perform(self, input: UseCaseInput) -> UseCaseResult:
        """Performs the operation defined by the use_case."""
        raise NotImplementedError

    def can_perform(self, input: UseCaseInput) -> UseCaseResult:
        """
        Check whether the operation defined by the use_case can be performed.

        True, by default.
        """
        return UseCaseResult(errors={}, data={})


StateId = t.NewType('StateId', str)
AccountId = t.NewType('AccountId', str)


class Process:
    schema: t.ClassVar[Schema]


class State:
    id: t.ClassVar[str]
    process: t.Type[Process]


class FlowUseCase(UseCase):
    """
    Describes multistage use case: such a case that can be performed with
    a few request. Has individual id & some inner state.
    """
    states: t.Dict[StateId, State]

    @property  # TODO: reify
    def interfaces(self):
        return {id_: s.process.schema for id_, s in self.states.items()}
