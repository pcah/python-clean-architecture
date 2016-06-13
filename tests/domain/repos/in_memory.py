# -*- coding: utf-8 -*-
import pytest

from dharma.domain.repos.in_memory import InMemoryRepository


class Super(object):
    def __init__(self, id):
        self.id = id


class Middle(Super):
    pass


class Sub(Middle):
    pass


sub_list = [Sub(id='sub1'), Sub(id='sub2')]
super_list = [Super(id='super')]


@pytest.fixture
def clear_all_repos(request):
    """Clears register of all created ConfigRepository instances"""
    request.addfinalizer(lambda: InMemoryRepository._clear_all_repos())


@pytest.yield_fixture
def super_repo():
    """
    Repository for class Super. Clears register of all created
    InMemoryRepository instances
    """
    yield InMemoryRepository(Super)
    InMemoryRepository._clear_all_repos()


@pytest.yield_fixture
def sub_repo():
    """
    Repository for class Sub. Clears register of all created
    InMemoryRepository instances
    """
    yield InMemoryRepository(Sub)
    InMemoryRepository._clear_all_repos()


@pytest.fixture
def sub_repo_loaded(sub_repo):
    """Repository for class Sub, loaded with some objects"""
    sub_repo.batch_save(sub_list)
    return sub_repo


@pytest.fixture
def super_repo_loaded(super_repo):
    """Repository for class Super, loaded with some objects"""
    super_repo.batch_save(super_list)
    return super_repo


def test_get_by_id(super_repo_loaded):
    """Object is gettable by its id"""
    obj = super_repo_loaded.get('super')
    assert obj.id == 'super'


def test_get_by_not_found(super_repo_loaded):
    """Getting unexisting object raises NotFound"""
    with pytest.raises(super_repo_loaded.NotFound):
        super_repo_loaded.get('fake_super')


def test_finding_super_repos(clear_all_repos):
    """InMemoryRepository finds repos of superclasses correctly"""
    super_repo = InMemoryRepository(Super)
    sub_repo = InMemoryRepository(Sub)
    assert sub_repo._klass_super_repos == [super_repo]


def test_finding_sub_repos(clear_all_repos):
    """InMemoryRepository finds repos of subclasses correctly
    NB: notice opposite order of repo creation.
    """
    sub_repo = InMemoryRepository(Sub)
    super_repo = InMemoryRepository(Super)
    assert sub_repo._klass_super_repos == [super_repo]


def test_existance_of_subclass_objs_in_super_repo(
        super_repo, sub_repo_loaded):
    """Instances of subclass are found in repos of its superclasses"""
    assert set(sub_repo_loaded.get_all()) == set(sub_list)
    assert set(super_repo.get_all()) == set(sub_list)


def test_nonexistance_of_superclass_entities_in_sub_repo(
        sub_repo, super_repo_loaded):
    """Instances of superclass can't be found in repos of its subclasses"""
    assert list(sub_repo.get_all()) == []
    assert set(super_repo_loaded.get_all()) == set(super_list)


def test_create_klass(mocker):
    """Repo `create` uses `klass` as a factory"""
    m = mocker.Mock()

    class A(object):
        def __init__(self, *args, **kwargs):
            m(*args, **kwargs)

    repo = InMemoryRepository(A)
    obj = repo.create('arg_value', kwarg_name='kwarg_value')
    assert obj
    m.assert_called_once_with('arg_value', kwarg_name='kwarg_value')


def test_create_factory(mocker):
    """Repo `create` uses `factory` as a factory"""
    class A(object):
        pass

    a = A()
    m = mocker.Mock(return_value=a)
    repo = InMemoryRepository(A, factory=m)
    obj = repo.create('arg_value', kwarg_name='kwarg_value')
    assert obj == a
    m.assert_called_once_with('arg_value', kwarg_name='kwarg_value')


def test_save(super_repo):
    """Object saved is stored in the repo"""
    obj = super_list[0]
    super_repo.save(obj)
    assert super_repo._register[obj.id] == obj


def test_create_and_save():
    """Repo `create_and_save`"""
    some_id = 'some id'
    class A(object):
        def __init__(self, id=some_id):
            self.id = id

    repo = InMemoryRepository(A)
    obj = repo.create_and_save(id=some_id)
    assert obj.id == some_id
    assert repo._register[some_id] == obj


def test_pop_exists(super_repo_loaded):
    """Repo pops an existing object"""
    id_ = super_list[0].id
    obj = super_repo_loaded.pop(id_)
    assert obj.id == id_


def test_filter_exist():
    """Repo returns filtered items"""
    # TODO


def test_filter_not_exist():
    """Repo returns nothing when elements are filtered out"""
    # TODO


def test_count_exist():
    """Repo counts filtered items"""
    # TODO


def test_count_not_exist():
    """Repo counts 0 items when items are filtered out"""
    # TODO


def test_pop_not_exists(super_repo_loaded):
    """Repo raises NotFound on popping not existing id"""
    with pytest.raises(super_repo_loaded.NotFound):
        super_repo_loaded.pop('not existing')


def test_remove_exists(super_repo_loaded):
    """Repo removes given object"""
    obj = super_list[0]
    super_repo_loaded.remove(obj)
    assert obj.id not in super_repo_loaded._register


def test_remove_not_exists(super_repo_loaded):
    """Repo raises NotFound on removing not existing id"""
    with pytest.raises(super_repo_loaded.NotFound):
        super_repo_loaded.remove(Super(id='not existing'))
