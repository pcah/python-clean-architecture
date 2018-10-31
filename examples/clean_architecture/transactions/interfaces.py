from haps import base, egg


@base
class IRequest:
    """Knows how to call a message from the source."""
    def call(self, **kwargs):
        """Make a message request."""


@base
class IConnector:
    """Knows how to call a message from the source."""
    def call(self, **kwargs):
        """Make a message request."""


@egg(profile='pyramid')
class WsgiRequest(IRequest):
    pass


@egg(profile='connector')
class I4sConnector(IConnector):

    request: IRequest

    def __getattr__(self, name):
        return lambda **kwargs: self.call(name, **kwargs)

    def call(self, name, **kwargs):
        method = getattr(self.connector_tech, name)
        return method(self.request, **kwargs)
