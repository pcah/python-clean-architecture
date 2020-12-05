import mock
import pytest

from pca.utils.dependency_injection import (
    Container,
    Scopes,
)


@pytest.fixture
def mock_container():
    return mock.Mock(spec=Container)


@pytest.fixture
def container():
    return Container(default_scope=Scopes.INSTANCE)
