from pca.utils.dependency_injection import Container as BaseContainer, Scopes


class Container(BaseContainer):

    def __init__(self, default_scope=Scopes.REQUEST, request_strategy=None):
        super().__init__(default_scope)
        # TODO #9. implement request scope
        self.request_strategy = request_strategy

    def load_from_file(self, path):
        # TODO #9. implement file configuration of DI Container
        raise NotImplementedError
