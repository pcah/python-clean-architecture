from pca.application.interactor import Interactor, RequestModel, ResponseModel
from pca.exceptions import ProcessError
from pca.utils.dependency_injection import Scopes

from examples.framework_ideas.dependency_injection import Container
from examples.framework_ideas.integrations import flask

# DI Container construction
container = Container(default_scope=Scopes.REQUEST, request_strategy=flask.FlaskRequestStrategy)
container.load_from_file('examples/config/di.yaml')


application = flask.PcaFlask('examples', container)


# noinspection PyAbstractClass
class BaseInteractor(Interactor):

    def handle_error(self, error: ProcessError, request: RequestModel) -> ResponseModel:
        return ResponseModel(data={}, errors={None: error.short_description})
