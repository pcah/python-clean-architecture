from pca.utils.imports import get_dotted_path


def test_get_dotted_path():
    assert get_dotted_path(get_dotted_path) == 'pca.utils.imports.get_dotted_path'
    assert get_dotted_path(str) == 'builtins.str'
    assert get_dotted_path(print) == 'builtins.print'
