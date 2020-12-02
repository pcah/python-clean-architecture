import pytest

from pca.utils.collections import Bunch


@pytest.fixture
def bunch():
    return Bunch()


@pytest.fixture
def bunch_foo():
    return Bunch(foo="bar")


def test_getattr(bunch_foo):
    assert bunch_foo.foo == "bar"
    with pytest.raises(AttributeError):
        # noinspection PyStatementEffect
        bunch_foo.bar


def test_getitem(bunch_foo):
    assert bunch_foo["foo"] == "bar"
    with pytest.raises(KeyError):
        # noinspection PyStatementEffect
        bunch_foo["bar"]


def test_setattr(bunch):
    bunch.foo = "bar"
    assert bunch["foo"] == "bar"


def test_setitem(bunch):
    bunch["foo"] = "bar"
    assert bunch.foo == "bar"


def test_delattr(bunch_foo):
    del bunch_foo.foo
    assert "foo" not in bunch_foo
    with pytest.raises(AttributeError):
        del bunch_foo.bar


def test_delitem(bunch_foo):
    del bunch_foo["foo"]
    assert "foo" not in bunch_foo
    with pytest.raises(KeyError):
        del bunch_foo["bar"]


def test_repr(bunch_foo):
    assert bunch_foo == eval(repr(bunch_foo))
