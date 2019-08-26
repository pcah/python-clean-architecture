from pathlib import Path

import pytest

from pca.utils.serialization import Loaders, load_from_filepath


@pytest.fixture
def ini_contents():
    ini_contents = "\n".join((
        "[pytest]",
        "python_files =",
        "    pca/**/tests/**/*.py",
        "    pca/**/tests/*.py",
        "    devops/**/tests/*.py",
        "python_functions = test_*",
        "# point this file as a source of coverage config",
        "addopts = --cov --cov-config=tox.ini --cov-fail-under=90 --tb=short",
    ))
    expected_contents = {
        'DEFAULT': {},
        'pytest': {
            'python_files': "\npca/**/tests/**/*.py\npca/**/tests/*.py\ndevops/**/tests/*.py",
            'python_functions': 'test_*',
            'addopts': '--cov --cov-config=tox.ini --cov-fail-under=90 --tb=short'
        }
    }
    return ini_contents, expected_contents


@pytest.fixture
def json_contents():
    json_contents = (
        '{"objects": [{"id": 1, "n": "foo"}, {"id": 2, "n": "bar"}, {"id": 3, "n": "baz"}]}'
    )
    expected_contents = {
        'objects': [
            {'id': 1, 'n': 'foo'},
            {'id': 2, 'n': 'bar'},
            {'id': 3, 'n': 'baz'},
        ]
    }
    return json_contents, expected_contents


@pytest.fixture
def yaml_contents():
    yaml_contents = "\n".join((
        "objects:",
        "  - id: 1",
        "    n: foo",
        "  - id: 2",
        "    n: bar",
        "  - id: 3",
        "    n: baz",
    ))
    expected_contents = {
        'objects': [
            {'id': 1, 'n': 'foo'},
            {'id': 2, 'n': 'bar'},
            {'id': 3, 'n': 'baz'},
        ]
    }
    return yaml_contents, expected_contents


def test_ini_chosen(fs, ini_contents):
    filepath = Path('foo.ini')
    ini_contents, expected_contents = ini_contents
    fs.create_file(filepath, contents=ini_contents)

    result = Loaders.ini(filepath)
    assert result == expected_contents


def test_ini_guessed(fs, ini_contents):
    filepath = Path('foo.ini')
    ini_contents, expected_contents = ini_contents
    fs.create_file(filepath, contents=ini_contents)

    result = Loaders.guess_loader(filepath)(filepath)
    assert result == expected_contents


def test_ini_from_filepath(fs, ini_contents):
    filepath = 'foo.ini'
    ini_contents, expected_contents = ini_contents
    fs.create_file(filepath, contents=ini_contents)

    result = load_from_filepath(filepath)
    assert result == expected_contents


def test_json_chosen(fs, json_contents):
    filepath = Path('foo.json')
    json_contents, expected_contents = json_contents
    fs.create_file(filepath, contents=json_contents)

    result = Loaders.json(filepath)
    assert result == expected_contents


def test_json_guessed(fs, json_contents):
    filepath = Path('foo.js')
    json_contents, expected_contents = json_contents
    fs.create_file(filepath, contents=json_contents)

    result = Loaders.guess_loader(filepath)(filepath)
    assert result == expected_contents


def test_json_from_filepath(fs, json_contents):
    filepath = 'foo.json'
    json_contents, expected_contents = json_contents
    fs.create_file(filepath, contents=json_contents)

    result = load_from_filepath(filepath)
    assert result == expected_contents


def test_yaml_chosen(fs, yaml_contents):
    filepath = Path('foo.yaml')
    yaml_contents, expected_contents = yaml_contents
    fs.create_file(filepath, contents=yaml_contents)

    result = Loaders.yaml(filepath)
    assert result == expected_contents


def test_yaml_guessed(fs, yaml_contents):
    filepath = Path('foo.yml')
    yaml_contents, expected_contents = yaml_contents
    fs.create_file(filepath, contents=yaml_contents)

    result = Loaders.guess_loader(filepath)(filepath)
    assert result == expected_contents


def test_yaml_from_filepath(fs, yaml_contents):
    filepath = 'foo.yaml'
    yaml_contents, expected_contents = yaml_contents
    fs.create_file(filepath, contents=yaml_contents)

    result = load_from_filepath(filepath)
    assert result == expected_contents
