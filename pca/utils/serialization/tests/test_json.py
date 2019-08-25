import mock

from pca.utils.serialization import json


def test_load_from_file():
    contents = '{"foo": {"bar": "baz", "spam": ["spam", "eggs", "spam"]}}'

    with mock.patch('pca.utils.serialization.json.read_from_file') as mocked_read_from_file:
        mocked_read_from_file.return_value = contents
        result = json.load_json_from_filepath('path/to/a/file.json')

    assert result == {'foo': {'bar': 'baz', 'spam': ['spam', 'eggs', 'spam']}}
    mocked_read_from_file.assert_called_with('path/to/a/file.json')
