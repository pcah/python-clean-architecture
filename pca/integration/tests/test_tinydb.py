# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from pca.data.predicate import where
from pca.exceptions import ConfigError, InvalidQueryError
from pca.integration.tinydb import TinyDbDao


@pytest.fixture(scope="session", autouse=True)
def tinydb():
    return pytest.importorskip("tinydb")


class TestConstruction:

    @pytest.fixture
    def path(self, tmpdir):
        return str(tmpdir.join('db.json'))

    @pytest.fixture
    def json_dao(self, mock_container, path):
        dao = TinyDbDao(mock_container, path=path, table_name='table_name')
        yield dao
        dao.clear_db_cache()

    def test_path(self, path, json_dao: TinyDbDao):
        assert json_dao._path == path
        assert Path(path).is_file()

    def test_implicit_json_storage(self, json_dao, tinydb):
        assert isinstance(json_dao._table._storage._storage, tinydb.storages.JSONStorage)

    def test_implicit_memory_storage(self, mock_container, tinydb):
        dao = TinyDbDao(mock_container, table_name='table_name')
        assert isinstance(dao._table._storage._storage, tinydb.storages.MemoryStorage)

    def test_db_cache(self, mock_container, path, json_dao: TinyDbDao):
        cache = TinyDbDao._db_cache
        assert cache.get(path) is json_dao._db
        second_dao = TinyDbDao(mock_container, path=path, table_name='another_table')
        assert second_dao._db is json_dao._db

    def test_no_table_name(self, mock_container):
        with pytest.raises(ConfigError) as e:
            TinyDbDao(mock_container)
        assert e.value.code == 'NO-TABLE-NAME-PROVIDED'


class TestApi:

    @pytest.fixture
    def dao(self, mock_container):
        """
        In-memory table that has three documents pre-assigned:
            {'char': 'a', 'is_a': True},
            {'char': 'b', 'is_a': False},
            {'char': 'c', 'is_a': False}
        """
        dao = TinyDbDao(mock_container, table_name='table_name')
        dao.batch_insert([
            {'char': c, 'is_a': c == 'a'}
            for c in 'abc'
        ])
        return dao

    # Dao.all
    def test_all(self, dao: TinyDbDao):
        assert list(dao.all()) == [
            {'char': 'a', 'is_a': True},
            {'char': 'b', 'is_a': False},
            {'char': 'c', 'is_a': False},
        ]

    # QueryChain.filter
    def test_multiple_filter_success(self, dao: TinyDbDao):
        not_a = ~(where('char') == 'a')
        c = where('char') == 'c'
        assert list(dao.filter(not_a).filter(c)) == [{'char': 'c', 'is_a': False}]

    # QueryChain.get
    def test_get_success(self, dao: TinyDbDao):
        assert dao.get(1) == {'char': 'a', 'is_a': True}

    def test_get_error(self, dao: TinyDbDao):
        with pytest.raises(dao.NotFound) as e:
            dao.get(42)
        assert e.value.area == 'REPO'
        assert e.value.code == 'NOT-FOUND'
        assert e.value.id_ == 42

    def test_filtered_get_success(self, dao: TinyDbDao):
        row_1 = dao.get(1)
        assert dao.filter(where('char') == 'a').get(1) == row_1

    def test_filtered_get_error(self, dao: TinyDbDao):
        with pytest.raises(dao.NotFound) as e:
            dao.filter(where('char') == 'a').get(2)
        assert e.value.area == 'REPO'
        assert e.value.code == 'NOT-FOUND'
        assert e.value.id_ == 2

    # QueryChain.get_or_none
    def test_get_or_none_success(self, dao: TinyDbDao):
        assert dao.get_or_none(1) == {'char': 'a', 'is_a': True}

    def test_get_or_none_fail(self, dao: TinyDbDao):
        assert dao.get_or_none(42) is None

    def test_filtered_get_or_none_success(self, dao: TinyDbDao):
        row_2 = dao.get(2)
        assert dao.filter(~(where('char') == 'a')).get_or_none(2) == row_2

    def test_filtered_get_or_none_fail(self, dao: TinyDbDao):
        assert dao.filter(~(where('char') == 'a')).get_or_none(1) is None

    # QueryChain.exists
    def test_exists_all_success(self, dao: TinyDbDao):
        assert dao.all().exists()

    def test_exists_empty_fail(self, dao: TinyDbDao):
        dao.clear()
        assert not dao.all().exists()

    def test_exists_filtered_success(self, dao: TinyDbDao):
        assert dao.filter(where('char') == 'c').exists()

    def test_exists_filtered_fail(self, dao: TinyDbDao):
        assert not dao.filter(where('char') == 'z').exists()

    # QueryChain.count
    def test_count_all(self, dao: TinyDbDao):
        assert dao.all().count() == 3

    def test_filtered_count(self, dao: TinyDbDao):
        assert dao.filter(~(where('char') == 'a')).count() == 2

    # QueryChain.update
    def test_update_all(self, dao: TinyDbDao):
        ids = dao.all().update({'char': 'z'})
        assert ids == [1, 2, 3]
        assert list(dao.all()) == [
            {'char': 'z', 'is_a': True},
            {'char': 'z', 'is_a': False},
            {'char': 'z', 'is_a': False},
        ]

    def test_update_filtered(self, dao: TinyDbDao):
        ids = dao.filter(~(where('char') == 'a')).update({'char': 'z'})
        assert ids == [2, 3]
        assert list(dao.all()) == [
            {'char': 'a', 'is_a': True},
            {'char': 'z', 'is_a': False},
            {'char': 'z', 'is_a': False},
        ]

    def test_update_none(self, dao: TinyDbDao):
        ids = dao.filter(where('char') == 'z').update({'char': 'a'})
        assert ids == []
        assert list(dao.all()) == [
            {'char': 'a', 'is_a': True},
            {'char': 'b', 'is_a': False},
            {'char': 'c', 'is_a': False},
        ]

    # QueryChain.remove
    def test_remove_all_error(self, dao: TinyDbDao):
        with pytest.raises(InvalidQueryError):
            dao.all().remove()

    def test_remove_filtered(self, dao: TinyDbDao):
        ids = dao.filter(where('char') == 'a').remove()
        assert ids == [1]
        assert list(dao.all()) == [
            {'char': 'b', 'is_a': False},
            {'char': 'c', 'is_a': False},
        ]

    def test_remove_none(self, dao: TinyDbDao):
        ids = dao.filter(where('char') == 'z').remove()
        assert ids == []
        assert list(dao.all()) == [
            {'char': 'a', 'is_a': True},
            {'char': 'b', 'is_a': False},
            {'char': 'c', 'is_a': False},
        ]

    # Dao.insert
    def test_insert(self, dao: TinyDbDao):
        id_ = dao.insert({'foo': 'bar'})
        assert id_ == 4

    # Dao.batch_insert
    def test_batch_insert(self, dao: TinyDbDao):
        batch = [{'foo': 'bar'}, {'foo': 'baz'}]
        result = dao.batch_insert(batch)
        assert result == (4, 5)
        assert list(dao.filter(where('foo').exists())) == batch

    # Dao.clear
    def test_clear(self, dao: TinyDbDao):
        dao.clear()
        assert list(dao.all()) == []
