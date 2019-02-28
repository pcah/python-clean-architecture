import typing as t

import pytest

from pca.data.dao import InMemoryDao
from pca.data.errors import QueryError, QueryErrors
from pca.data.predicate import where


pred_a = where('char') == 'a'
pred_not_a = ~(where('char') == 'a')
pred_c = where('char') == 'c'
pred_z = where('char') == 'z'


def get_ids(objects: t.Iterable):
    return [dto.id for dto in objects]


@pytest.fixture
def content():
    return [{'char': c, 'is_a': c == 'a'} for c in 'abc']


class TestConstruction:

    def test_initial_content(self, mock_container, content):
        dao = InMemoryDao(mock_container, initial_content=content)
        assert list(dao.all()) == content


class TestApi:

    @pytest.fixture
    def dao(self, mock_container, content):
        """
        In-memory table that has three documents pre-assigned:
            {'char': 'a', 'is_a': True},
            {'char': 'b', 'is_a': False},
            {'char': 'c', 'is_a': False}
        """
        dao = InMemoryDao(mock_container, initial_content=content)
        return dao

    # Dao.all
    def test_all(self, dao: InMemoryDao):
        assert get_ids(dao.all()) == [1, 2, 3]

    # QueryChain.filter
    def test_multiple_filter_success(self, dao: InMemoryDao):
        assert list(dao.filter(pred_not_a).filter(pred_c)) == [{'char': 'c', 'is_a': False}]

    # QueryChain.filter_by
    def test_filter_by_success(self, dao: InMemoryDao):
        assert list(dao.filter(pred_not_a).filter_by(id_=3)) == [{'char': 'c', 'is_a': False}]

    def test_filter_by_both_arguments_error(self, dao: InMemoryDao):
        with pytest.raises(QueryError):
            assert dao.all().filter_by(id_=3, ids=[3, 5])

    def test_filter_by_two_times_error(self, dao: InMemoryDao):
        with pytest.raises(QueryError):
            assert dao.all().filter_by(id_=3).filter_by(id_=5)

    # QueryChain.get
    def test_get_success(self, dao: InMemoryDao):
        assert dao.get(1) == {'char': 'a', 'is_a': True}

    def test_get_fail(self, dao: InMemoryDao):
        assert dao.get(42) is None

    def test_filtered_get_success(self, dao: InMemoryDao):
        object_2 = dao.get(2)
        assert dao.filter(pred_not_a).get(2) == object_2

    def test_filtered_get_fail(self, dao: InMemoryDao):
        assert dao.filter(pred_not_a).get(1) is None

    # QueryChain.exists
    def test_exists_all_success(self, dao: InMemoryDao):
        assert dao.all().exists()

    def test_exists_empty_fail(self, dao: InMemoryDao):
        dao.clear()
        assert not dao.all().exists()

    def test_exists_filtered_success(self, dao: InMemoryDao):
        assert dao.filter(pred_c).exists()

    def test_exists_filtered_fail(self, dao: InMemoryDao):
        assert not dao.filter(pred_z).exists()

    # QueryChain.count
    def test_count_all(self, dao: InMemoryDao):
        assert dao.all().count() == 3

    def test_filtered_count(self, dao: InMemoryDao):
        assert dao.filter(pred_not_a).count() == 2

    # QueryChain.update
    def test_update_all(self, dao: InMemoryDao):
        ids = dao.all().update(char='z')
        assert ids == [1, 2, 3]
        assert list(dao.all()) == [
            {'char': 'z', 'is_a': True},
            {'char': 'z', 'is_a': False},
            {'char': 'z', 'is_a': False},
        ]

    def test_update_filtered(self, dao: InMemoryDao):
        ids = dao.filter(pred_not_a).update(char='z')
        assert ids == [2, 3]
        assert list(dao.all()) == [
            {'char': 'a', 'is_a': True},
            {'char': 'z', 'is_a': False},
            {'char': 'z', 'is_a': False},
        ]

    def test_update_filtered_by_id(self, dao: InMemoryDao):
        ids = dao.filter(pred_not_a).filter_by(id_=2).update(char='z')
        assert ids == [2]
        assert list(dao.all()) == [
            {'char': 'a', 'is_a': True},
            {'char': 'z', 'is_a': False},
            {'char': 'c', 'is_a': False},
        ]

    def test_update_none(self, dao: InMemoryDao):
        ids = dao.filter(pred_z).update(char='z')
        assert ids == []
        assert list(dao.all()) == [
            {'char': 'a', 'is_a': True},
            {'char': 'b', 'is_a': False},
            {'char': 'c', 'is_a': False},
        ]

    # QueryChain.remove
    def test_remove_all_error(self, dao: InMemoryDao):
        with pytest.raises(QueryError) as error_info:
            dao.all().remove()
        assert error_info.value == QueryErrors.UNRESTRICTED_REMOVE

    def test_remove_filtered(self, dao: InMemoryDao):
        ids = dao.filter(pred_a).remove()
        assert ids == [1]
        assert get_ids(dao.all()) == [2, 3]

    def test_remove_filtered_by_id(self, dao: InMemoryDao):
        ids = dao.filter(pred_not_a).filter_by(id_=2).remove()
        assert ids == [2]
        assert get_ids(dao.all()) == [1, 3]

    def test_remove_none(self, dao: InMemoryDao):
        ids = dao.filter(pred_z).remove()
        assert ids == []
        assert get_ids(dao.all()) == [1, 2, 3]

    # Dao.filter_by
    def test_dao_filter_by_success(self, dao: InMemoryDao):
        assert list(dao.filter_by(id_=3)) == [{'char': 'c', 'is_a': False}]

    def test_dao_filter_by_both_arguments_error(self, dao: InMemoryDao):
        with pytest.raises(QueryError):
            assert dao.filter_by(id_=3, ids=[3, 5])

    def test_dao_filter_by_two_times_error(self, dao: InMemoryDao):
        with pytest.raises(QueryError):
            assert dao.filter_by(id_=3).filter_by(id_=5)

    # Dao.insert
    def test_insert(self, dao: InMemoryDao):
        id_ = dao.insert(foo='bar')
        assert id_ == 4

    # Dao.batch_insert
    def test_batch_insert(self, dao: InMemoryDao):
        batch = [{'foo': 'bar'}, {'foo': 'baz'}]
        result = dao.batch_insert(batch)
        assert result == (4, 5)
        assert list(dao.filter(where('foo').exists())) == batch

    # Dao.clear
    def test_clear(self, dao: InMemoryDao):
        dao.clear()
        assert list(dao.all()) == []
