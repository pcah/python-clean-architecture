# -*- coding: utf-8 -*-
import mock
import pytest

from pca.utils.dependency_injection import Container


@pytest.fixture
def mock_container():
    return mock.Mock(spec=Container)
