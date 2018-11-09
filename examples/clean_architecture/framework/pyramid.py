# -*- coding: utf-8 -*-
import typing as t

from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from .dependency_injection import AbstractContainer
from .logic import LogicError
from .use_case import UseCase, UseCaseInput, UseCaseResult


class PyramidContainer(AbstractContainer):
    """Knows how to construct Pyramid specific dependencies."""

    request: Request

    def __init__(self, request: Request):
        self._request = request


class PyramidResource:
    """
    This is HTTP-specific part of the application. It responses to all
    the `GET`s and `POST`s and knows how to HTML/JSON. It may be CRUD-like
    or respect the Command-Query Responsibility Segregation.

    For the sake of simplicity, let's assume that responses are AJAX.
    """
    USE_CASE: t.ClassVar[t.Type[UseCase]]
    request: Request

    def __init_subclass__(cls, **kwargs):
        cls.get = view_config(renderer='json')(cls.get)
        cls.post = view_config(renderer='json')(cls.post)

    @reify
    def dic(self):
        return PyramidContainer(self.request)

    @reify
    def use_case(self):
        return self.USE_CASE(self.dic)

    def build_input(self, request) -> UseCaseInput:
        """Build use case input data object based on the HTTP request."""
        raise NotImplementedError

    def build_response(self, data: UseCaseResult) -> dict:
        """Build HTTP response based on result got from UseCase."""
        raise NotImplementedError

    def build_error_response(self, errors: t.Dict[str, LogicError]) -> dict:
        """Build HTTP response based on an errors raised by UseCase."""
        raise NotImplementedError

    def get(self, request: Request) -> Response:
        """HTTP GET"""
        input = self.build_input(request)
        try:
            result = self.use_case.can_process(input)
        except LogicError as e:
            # TODO is it reasonable that use case can just raise an LogicError?
            return self.build_error_response({'': e})
        return self.build_response(result)

    def post(self, request: Request) -> Response:
        """HTTP POST"""
        input = self.build_input(request)
        try:
            result = self.use_case.process(input)
        except LogicError as e:
            # TODO is it reasonable that use case can just raise an LogicError?
            return self.build_error_response({'': e})
        return self.build_response(result)
