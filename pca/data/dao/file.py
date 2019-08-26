from pca.data.errors import QueryErrors
from pca.utils.collections import iterate_over_values, sget
from pca.utils.dependency_injection import Container, Scopes, scope
from pca.utils.serialization import load_from_filepath

from .in_memory import InMemoryDao


@scope(Scopes.SINGLETON)
class FileDao(InMemoryDao):

    def __init__(self, container: Container, filepath: str, path: str = None):
        content = load_from_filepath(filepath)
        self.path = path
        if path:
            content = sget(content, path)
        content = list(iterate_over_values(content))
        super().__init__(container, initial_content=content)

    def __not_implemented__(self, *args, **kwargs):
        raise QueryErrors.IMMUTABLE_DAO

    # TODO Liskov violation, refactor needed
    _resolve_update = _resolve_remove = insert = batch_insert = clear = __not_implemented__
