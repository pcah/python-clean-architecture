# -*- coding: utf-8 -*-
import typing as t
from dataclasses import dataclass

from marshmallow import Schema

from pca.utils.functools import reify

from examples.clean_architecture.framework import UseCaseInterface
from .use_case import UseCaseInput, UseCase


FlowId = t.NewType("FlowId", str)
StateId = t.NewType("StateId", str)


@dataclass
class FlowUseCaseInput(UseCaseInput):
    flow_id: t.Optional[str] = None
    state_id: t.Optional[str] = None


@dataclass
class FlowUseCaseInterface(UseCaseInterface):
    state_id: str


class Process:
    schema: t.ClassVar[Schema]


class State:
    id: t.ClassVar[str]
    process: t.Type[Process]

    @property
    def schema(self):
        return self.process.schema

    @property
    def data(self):
        return {}


# noinspection PyAbstractClass
class FlowUseCase(UseCase):
    """
    Describes multistage use-case: such a case that has to be executed with
    a few request. Has individual id & some inner state.
    """
    states: t.Dict[StateId, State]
    flow_id: FlowId
    action: str = None  # TODO ?

    @reify
    def interfaces(self):
        return [
            FlowUseCaseInterface(schema=state.schema, action=self.action, state_id=state_id)
            for state_id, state in self.states.items()
        ]
