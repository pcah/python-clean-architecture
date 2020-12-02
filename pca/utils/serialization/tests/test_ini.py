import pytest

from pca.utils.serialization import load_ini_from_filepath


@pytest.fixture
def contents():
    ini_contents = "\n".join(
        (
            "[pytest]",
            "python_files =",
            "    pca/**/tests/**/*.py",
            "    pca/**/tests/*.py",
            "    devops/**/tests/*.py",
            "python_functions = test_*",
            "# point this file as a source of coverage config",
            "addopts = --cov --cov-config=tox.ini --cov-fail-under=90 --tb=short",
        )
    )
    expected_contents = {
        "DEFAULT": {},
        "pytest": {
            "python_files": "\npca/**/tests/**/*.py\npca/**/tests/*.py\ndevops/**/tests/*.py",
            "python_functions": "test_*",
            "addopts": "--cov --cov-config=tox.ini --cov-fail-under=90 --tb=short",
        },
    }
    return ini_contents, expected_contents


def test_load_ini_from_filepath(fs, contents):
    filepath = "foo.ini"
    ini_contents, expected_contents = contents
    fs.create_file(filepath, contents=ini_contents)

    result = load_ini_from_filepath(filepath)

    assert result == expected_contents
