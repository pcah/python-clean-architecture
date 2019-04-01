import pytest

from devops.utils import os


@pytest.mark.parametrize("pattern, substitute, text, expected", [
    (
        # pattern
        r"(?<=</sub>\n)\n(?=\n)",
        # substitute
        "\n* 1\n* 2\n",
        # text
        "\n".join((
            "<sub>some text</sub>",
            "",
            "",
            "",
        )),
        # expected
        "\n".join((
            "<sub>some text</sub>",
            "",
            "* 1",
            "* 2",
            "",
            "",
        )),
    ),
    (
        # pattern
        r"(?<=VERSION = )Version\([^)]*\)(?=\n)",
        # substitute
        "Version(1, 0, 0, 'a', 0)",
        # text
        "\n".join((
            "PACKAGE_NAME = 'pca'",
            "VERSION = Version(0, 0, 2)",
            "",
            "PACKAGE_DIR = path.dirname(__file__)",
        )),
        # expected
        "\n".join((
            "PACKAGE_NAME = 'pca'",
            "VERSION = Version(1, 0, 0, 'a', 0)",
            "",
            "PACKAGE_DIR = path.dirname(__file__)",
        )),
    )
])
def test_replace_in_multiline_string(pattern, substitute, text, expected):
    result = os.replace_in_multiline_string(pattern, substitute, text)
    assert result == expected


@pytest.mark.parametrize("contents, pattern, substitute, expected", [
    (
        "foo\n1\n2\nbar",
        "1\n2",
        "a\nb\nc",
        "foo\na\nb\nc\nbar",
    ),
])
def test_replace_in_file(fs, contents, pattern, substitute, expected):
    filepath = 'tmp/test_file'
    fs.create_file(filepath)
    with open(filepath, 'w') as f:
        f.write(contents)

    os.replace_in_file(filepath, pattern, substitute)

    with open(filepath) as f:
        result = f.read()
    assert result == expected
