from flask import Flask


class PcaFlask(Flask):
    def __init__(self, import_name, container, **kwargs):
        super().__init__(import_name, **kwargs)
        self.container = container

    def controller(self, route_name, template):
        """
        Function decorator factory that introduces Controller pattern into integration with Flask.
        """

        def decorator(wrapped):
            # TODO #52. implementation
            return self.route(wrapped)

        return decorator


class FlaskRequestStrategy:
    """A strategy that knows how to bind DI relations in the scope of Flask's request class """

    # TODO #52. implementation
