from examples.framework.dependency_injection import Container, Scopes
from examples.framework.integrations.django import DjangoSessionStrategy


container = Container(default_scope=Scopes.REQUEST, request_strategy=DjangoSessionStrategy)
container.load_from_file('examples/config/di.yaml')
