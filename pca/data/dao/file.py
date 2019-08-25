from pca.data.errors import QueryErrors
from pca.utils.dependency_injection import Container, Scopes, scope
from pca.utils.serialization import load_yaml_from_filepath

from .in_memory import InMemoryDao


@scope(Scopes.SINGLETON)
class FileDao(InMemoryDao):

    def __init__(self, container: Container, filepath: str, path: str):
        initial_content = load_yaml_from_filepath(filepath)

        super().__init__(container, initial_content=initial_content)

    def __not_implemented__(self, *args, **kwargs):
        raise QueryErrors.IMMUTABLE_DAO

    _resolve_update = _resolve_remove = insert = batch_insert = clear = __not_implemented__
