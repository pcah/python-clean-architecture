from itertools import chain
import pytest

from pca.utils.collections import get_duplicates


@pytest.mark.parametrize(
    "iterable, expected",
    [
        (set(), set()),
        ((1, 1), set([1])),
        ((1, 2), set()),
        (["a", "a", "b", "a"], set(["a"])),
        ("", set()),
        ("abbcddde", set(["b", "d"])),
        (range(4), set()),
        (chain(range(6), range(0, 6, 2)), set([0, 2, 4])),
    ],
    ids=[
        "empty set",
        "simple tuple with duplication",
        "simple tuple without duplication",
        "list of strings",
        "empty string",
        "string with duplicated chars",
        "generator with unique values",
        "generator stepped by 2",
    ],
)
def test_get_duplicates(iterable, expected):
    assert expected == get_duplicates(iterable)
