# -*- coding: utf-8 -*-
import typing as t

from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from pca.utils.functools import reify

from .dependency_injection import AbstractContainer
from .logic import LogicError, ValidationError
from .use_case import UseCase, UseCaseInput, UseCaseResult


class PyramidContainer(AbstractContainer):
    """Knows how to construct Pyramid specific dependencies."""

    request: Request

    def __init__(self, request: Request):
        self._request = request


class PyramidResource:
    """
    This is HTTP-specific part of the application. It responses to all
    the `GET`s and `POST`s and knows how to talk in HTML/JSON.
    It may be CRUD-like or respect the Command-Query Responsibility
    Segregation.

    For the sake of simplicity, let's assume that responses are all AJAX.
    """
    use_case_class: t.ClassVar[t.Type[UseCase]]
    route: t.ClassVar[str]
    get_action: t.ClassVar[str] = 'can_execute'
    post_action: t.ClassVar[str] = 'execute'
    request: Request

    def __init_subclass__(cls, **kwargs):
        """Register routes"""
        super().__init_subclass__(**kwargs)
        route_name = cls.route
        kwargs = dict(renderer='json', route_name=route_name)
        cls.get = view_config(request_method='GET', **kwargs)(cls.get)
        cls.post = view_config(request_method='POST', **kwargs)(cls.post)
        cls.routing = {
            'get': {'request_method': 'GET', 'route_name': route_name},
            'post': {'request_method': 'POST', 'route_name': route_name},
        }

    @reify
    def container(self):
        return PyramidContainer(self.request)

    @reify
    def use_case(self):
        return self.use_case_class(self.container)

    def get(self, request: Request) -> Response:
        """HTTP GET"""
        action = getattr(self.use_case, self.get_action)
        return self.handle(action, request)

    def post(self, request: Request) -> Response:
        """HTTP POST"""
        action = getattr(self.use_case, self.post_action)
        return self.handle(action, request)

    def handle(self, action, request: Request) -> Response:
        """
        Actual request handler. Calls the use-case and builds the HTTP Response.
        """
        input = self.handle_request(request)
        try:
            result = action(input)
        except (LogicError, ValidationError) as e:
            return self.handle_error(e)
        return self.handle_response(result)

    def handle_request(self, request) -> UseCaseInput:
        """Build use case input data object based on the HTTP request."""
        raise NotImplementedError

    def handle_response(self, data: UseCaseResult) -> Response:
        """Build HTTP response based on result got from use-case."""
        raise NotImplementedError

    def handle_error(self, errors: Exception) -> Response:
        """Build HTTP response based on an errors raised by use-case."""
        raise NotImplementedError


# noinspection PyPep8Naming
class register_rest_view_set:
    def __init__(self, item_route=None, collection_route=None):
        self.kwargs = {'_depth': 1, 'renderer': 'json'}
        if item_route:
            self.routing = dict(
                read_item={'request_method': 'GET', 'route_name': item_route},
                update_item={'request_method': 'PUT', 'route_name': item_route},
                delete_item={'request_method': 'DELETE', 'route_name': item_route},
            )
        else:
            self.routing = {}
        if collection_route:
            self.routing.update(
                list_items={'request_method': 'GET', 'route_name': collection_route},
                create_item={'request_method': 'POST', 'route_name': collection_route},
            )

    def __call__(self, cls):
        for method, route in self.routing.items():
            if hasattr(cls, method):
                cls = view_config(attr=method, **self.kwargs, **route)
            else:
                self.routing.pop(method)
        cls.routing = self.routing
        return cls


@register_rest_view_set(item_route='foo', collection_route='foos')
class RestViewSet:

    def __init__(self, request):
        self.request = request

    def read_item(self):
        raise NotImplementedError

    def update_item(self):
        raise NotImplementedError

    def delete_item(self):
        raise NotImplementedError

    def create_item(self):
        raise NotImplementedError

    def list_items(self):
        raise NotImplementedError
