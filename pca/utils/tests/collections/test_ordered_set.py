import pickle

import pytest

from pca.utils.collections import OrderedSet


def test_pickle():
    set1 = OrderedSet("abracadabra")
    roundtrip = pickle.loads(pickle.dumps(set1))
    assert roundtrip == set1


def test_empty_pickle():
    empty_oset = OrderedSet()
    empty_roundtrip = pickle.loads(pickle.dumps(empty_oset))
    assert empty_roundtrip == empty_oset


def test_order():
    set1 = OrderedSet("abracadabra")
    assert len(set1) == 5
    assert set1 == OrderedSet(["a", "b", "r", "c", "d"])
    assert list(reversed(set1)) == ["d", "c", "r", "b", "a"]


def test_binary_operations():
    set1 = OrderedSet("abracadabra")
    set2 = OrderedSet("simsalabim")
    assert set1 != set2

    assert set1 & set2 == OrderedSet(["a", "b"])
    assert set1 | set2 == OrderedSet(["a", "b", "r", "c", "d", "s", "i", "m", "l"])
    assert set1 - set2 == OrderedSet(["r", "c", "d"])


def test_indexing():
    set1 = OrderedSet("abracadabra")
    assert set1[:] == set1
    assert set1.copy() == set1
    assert set1[:] is set1
    assert set1.copy() is not set1

    assert set1[[1, 2]] == OrderedSet(["b", "r"])
    assert set1[1:3] == OrderedSet(["b", "r"])
    assert set1.index("b") == 1
    assert set1.index(["b", "r"]) == [1, 2]

    with pytest.raises(KeyError):
        set1.index("br")


def test_tuples():
    set1 = OrderedSet()
    tup = ("tuple", 1)
    set1.add(tup)
    assert set1.index(tup) == 0
    assert set1[0] == tup


def test_remove():
    set1 = OrderedSet("abracadabra")

    set1.remove("a")
    set1.remove("b")

    assert set1 == OrderedSet("rcd")
    assert set1[0] == "r"
    assert set1[1] == "c"
    assert set1[2] == "d"

    assert set1.index("r") == 0
    assert set1.index("c") == 1
    assert set1.index("d") == 2

    assert "a" not in set1
    assert "b" not in set1
    assert "r" in set1

    # Make sure we can .discard() something that's already gone, plus
    # something that was never there
    set1.discard("a")
    set1.discard("a")


def test_remove_error():
    # If we .remove() an element that's not there, we get a KeyError
    set1 = OrderedSet("abracadabra")
    with pytest.raises(KeyError):
        set1.remove("z")


def test_clear():
    set1 = OrderedSet("abracadabra")
    set1.clear()

    assert len(set1) == 0
    assert set1 == OrderedSet()


def test_update():
    set1 = OrderedSet("abcd")
    result = set1.update("efgh")

    assert result == 7
    assert len(set1) == 8
    assert "".join(set1) == "abcdefgh"

    set2 = OrderedSet("abcd")
    result = set2.update("cdef")
    assert result == 5
    assert len(set2) == 6
    assert "".join(set2) == "abcdef"


def test_pop():
    set1 = OrderedSet("ab")
    elem = set1.pop()

    assert elem == "b"
    elem = set1.pop()

    assert elem == "a"

    with pytest.raises(KeyError):
        set1.pop()
