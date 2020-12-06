import pytest

from devops.utils.version import Version


@pytest.mark.parametrize(
    "params, expected",
    [
        ((1, 0), (1, 0)),
        ((1, 0, None), (1, 0)),
        ((1, 2, 0), (1, 2, 0)),
        ((0, 1, 2, "a", 1), (0, 1, 2)),
        ((1, 0, None, "a", 0), (1, 0)),
    ],
)
def test_as_release(params, expected):
    assert Version(*params).as_release() == expected


@pytest.mark.parametrize(
    "params, expected",
    [
        ((1, 0), "Version(1, 0)"),
        ((1, 2, 0), "Version(1, 2, 0)"),
        ((1, 2, 3), "Version(1, 2, 3)"),
        ((0, 1, 2, "a", 1), "Version(0, 1, 2, 'a', 1)"),
        ((1, 0, None, "a", 0), "Version(1, 0, None, 'a', 0)"),
    ],
)
def test_repr(params, expected):
    assert repr(Version(*params)) == expected


@pytest.mark.parametrize(
    "params, expected",
    [
        ((1, 0), "1.0"),
        ((1, 0, None), "1.0"),
        ((1, 2, 0), "1.2.0"),
        ((0, 1, 2, "a", 1), "0.1.2a1"),
        ((1, 0, None, "a", 0), "1.0a0"),
    ],
)
def test_as_string(params, expected):
    assert Version(*params).as_string() == expected


@pytest.mark.parametrize(
    "params, expected",
    [
        ((1, 0), "v1.0"),
        ((1, 0, None), "v1.0"),
        ((1, 2, 0), "v1.2.0"),
        ((0, 1, 2, "a", 1), "v0.1.2a1"),
        ((1, 0, None, "a", 0), "v1.0a0"),
    ],
)
def test_as_git_tag(params, expected):
    assert Version(*params).as_git_tag() == expected


@pytest.mark.parametrize(
    "method",
    [
        Version.bump_major,
        Version.bump_minor,
        Version.bump_micro,
    ],
)
def test_bumping_non_final(method):
    version = Version(1, 2, 3, "a", 3)
    with pytest.raises(AssertionError):
        method(version)


@pytest.mark.parametrize(
    "method",
    [
        Version.bump_pre,
        Version.promote_pre,
    ],
)
def test_promoting_final(method):
    version = Version(1, 2, 3)
    with pytest.raises(AssertionError):
        # noinspection PyArgumentList
        method(version)


@pytest.mark.parametrize(
    "version, add_pre, expected",
    [
        (Version(1, 2, 3), True, Version(2, 0, 0, "a", 0)),
        (Version(1, 2, 3), False, Version(2, 0, 0)),
        (Version(0, 2, None), True, Version(1, 0, None, "a", 0)),
        (Version(0, 2, None), False, Version(1, 0)),
    ],
)
def test_bump_major(version, add_pre, expected):
    assert version.bump_major(add_pre=add_pre) == expected


@pytest.mark.parametrize(
    "version, add_pre, expected",
    [
        (Version(0, 0), True, Version(0, 1, None, "a", 0)),
        (Version(0, 0), False, Version(0, 1)),
        (Version(1, 2, 3), True, Version(1, 3, 0, "a", 0)),
        (Version(1, 2, 3), False, Version(1, 3, 0)),
        (Version(0, 2, None), True, Version(0, 3, None, "a", 0)),
        (Version(0, 2, None), False, Version(0, 3)),
    ],
)
def test_bump_minor(version, add_pre, expected):
    assert version.bump_minor(add_pre=add_pre) == expected


@pytest.mark.parametrize(
    "version, add_pre, expected",
    [
        (Version(0, 0), True, Version(0, 0, 1)),
        (Version(0, 0), False, Version(0, 0, 1)),
        (Version(1, 2, 3), True, Version(1, 2, 4)),
        (Version(1, 2, 3), False, Version(1, 2, 4)),
        (Version(0, 2, None), True, Version(0, 2, 1)),
        (Version(0, 2, None), False, Version(0, 2, 1)),
    ],
)
def test_bump_micro(version, add_pre, expected):
    assert version.bump_micro(add_pre=add_pre) == expected


@pytest.mark.parametrize(
    "version, expected",
    [
        (Version(1, 2, 3, "b", 0), Version(1, 2, 3, "b", 1)),
        (Version(0, 2, None, "a", 4), Version(0, 2, None, "a", 5)),
    ],
)
def test_bump_pre(version, expected):
    assert version.bump_pre() == expected


@pytest.mark.parametrize(
    "version, expected",
    [
        (Version(1, 2, 3, "b", 0), Version(1, 2, 3, "rc", 0)),
        (Version(0, 2, None, "a", 4), Version(0, 2, None, "b", 0)),
        (Version(0, 2, 0, "rc", 4), Version(0, 2, 0)),
    ],
)
def test_promote_pre(version, expected):
    assert version.promote_pre() == expected
