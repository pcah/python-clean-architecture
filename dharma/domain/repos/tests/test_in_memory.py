# -*- coding: utf-8 -*-
import mock
import pytest

from dharma.data.formulae import where
from dharma.domain.repos.in_memory import InMemoryRepository
from dharma.utils import serialization


class Super(object):
    """This class is intended for super_repo"""
    attr_1 = 'attr_1'

    def __init__(self, id_):
        self.id = id_
        self.attr_2 = 'attr_2_super'


class Middle(Super):
    """This class has no repo."""
    pass


class Sub(Middle):
    """This class is intended for sub_repo"""
    def __init__(self, id_):
        super(Sub, self).__init__(id_)
        self.attr_2 = 'attr_2_sub'


sub_list = (Sub(id_='sub1'), Sub(id_='sub2'))
super_id = 'super'
super_obj = Super(id_=super_id)
super_list = (super_obj,)


@pytest.fixture(autouse=True)
def clear_all_repos():
    """Clears register of all created ConfigRepository instances"""
    yield
    InMemoryRepository._clear_all_repos()


@pytest.fixture
def super_repo():
    """
    Repository for class Super. Clears register of all created
    InMemoryRepository instances
    """
    yield InMemoryRepository(Super)
    InMemoryRepository._clear_all_repos()


@pytest.fixture
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
    sub_repo.batch_insert(sub_list)
    return sub_repo


@pytest.fixture
def super_repo_loaded(super_repo):
    """Repository for class Super, loaded with some objects"""
    super_repo.batch_insert(super_list)
    return super_repo


@pytest.fixture(scope='session')
def predicate_attr_2_super():
    return where('attr_2') == 'attr_2_super'


@pytest.fixture(scope='session')
def predicate_attr_2_sub():
    return (where('attr_1') == 'attr_1') & (where('attr_2') == 'attr_2_sub')


@pytest.fixture(scope='session')
def predicate_foo_bar():
    return where('foo') == 'bar'


def test_get(super_repo_loaded):
    """Object is gettable by its id"""
    obj = super_repo_loaded.get(super_id)
    assert obj.id == super_id


def test_get_not_found(super_repo_loaded):
    """Getting unexisting object raises NotFound"""
    with pytest.raises(super_repo_loaded.NotFound):
        super_repo_loaded.get('not existing')


def test_get_or_none(super_repo_loaded):
    """Object is gettable by its id"""
    obj = super_repo_loaded.get_or_none(super_id)
    assert obj.id == super_id


def test_get_or_none_not_found(super_repo_loaded):
    """Getting unexisting object raises NotFound"""
    assert super_repo_loaded.get_or_none('not existing') is None


def test_class_register(super_repo):
    other_super_repo = InMemoryRepository(Super)
    assert super_repo.all() == other_super_repo.all()


@pytest.mark.usefixtures("clear_all_repos")
def test_finding_super_repos():
    """InMemoryRepository finds repos of superclasses correctly"""
    InMemoryRepository(Super)
    sub_repo = InMemoryRepository(Sub)
    sub_repo_super_klasses = sub_repo._SUPER_KLASSES_WITH_REPO[sub_repo._klass_qualname]
    assert sub_repo_super_klasses == ['test_in_memory.Super']


@pytest.mark.usefixtures("clear_all_repos")
def test_finding_sub_repos():
    """InMemoryRepository finds repos of subclasses correctly
    NB: notice opposite order of repo creation.
    """
    sub_repo = InMemoryRepository(Sub)
    InMemoryRepository(Super)
    sub_repo_super_klasses = sub_repo._SUPER_KLASSES_WITH_REPO[sub_repo._klass_qualname]
    assert sub_repo_super_klasses == ['test_in_memory.Super']


def test_existance_of_subclass_objs_in_super_repo(
        super_repo, sub_repo_loaded):
    """Instances of subclass are found in repos of its superclasses"""
    assert set(sub_repo_loaded.all()) == set(sub_list)
    assert set(super_repo.all()) == set(sub_list)


def test_nonexistance_of_superclass_entities_in_sub_repo(
        sub_repo, super_repo_loaded):
    """Instances of superclass can't be found in repos of its subclasses"""
    assert list(sub_repo.all()) == []
    assert set(super_repo_loaded.all()) == set(super_list)


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


def test_insert(super_repo):
    """Object inserted is stored in the repo"""
    super_repo.insert(super_obj)
    assert super_repo.get(super_id) is super_obj


def test_create_and_insert():
    """Repo `create_and_insert`"""
    some_id = 12

    class A(object):
        def __init__(self, id_=some_id):
            self.id = id_

    repo = InMemoryRepository(A)
    obj = repo.create_and_insert(id_=some_id)
    assert obj.id == some_id
    assert repo.get(some_id) is obj


def test_update():
    """Repo `update`"""
    some_id = 12

    class A(object):
        def __init__(self, id_=some_id):
            self.id = id_

    repo = InMemoryRepository(A)
    obj = repo.create_and_insert(id_=some_id)
    new_obj = A(some_id)
    success = repo.update(new_obj)
    assert success
    assert new_obj is not obj
    assert repo.get(some_id) is new_obj


def test_batch_update():
    """Repo `update`"""
    some_id = 12

    class A(object):
        def __init__(self, id_=some_id):
            self.id = id_

    repo = InMemoryRepository(A)
    objs = {id_: repo.create_and_insert(id_=id_) for id_ in range(6)}
    new_objs = [A(id_) for id_ in range(7)]
    success = repo.batch_update(new_objs)
    assert all(success[id_] for id_ in range(6))  # old instances has been updated
    assert not success[6]  # the new instance #6 hasn't been already in repo so it raised an error
    assert all(repo.get(id_) is new_objs[id_] for id_ in range(6))
    with pytest.raises(InMemoryRepository.NotFound):
        assert repo.get(6)  # and still the #6 is not there


def test_pop_exists(super_repo_loaded):
    """Repo pops an existing object"""
    obj = super_repo_loaded.pop(super_id)
    assert obj.id == super_id


def test_exists(super_repo_loaded):
    """Repo checks whether object exists"""
    assert super_repo_loaded.exists(super_id)


def test_not_exists(super_repo_loaded):
    """Repo checks whether object exists"""
    assert not super_repo_loaded.exists('not existing')


@pytest.mark.usefixtures("sub_repo_loaded")
def test_filter_exist(super_repo_loaded, predicate_attr_2_sub, predicate_attr_2_super):
    """Repo returns filtered items"""
    assert set(super_repo_loaded.filter(predicate_attr_2_super)) == set(super_list)
    assert set(super_repo_loaded.filter(predicate_attr_2_sub)) == set(sub_list)


@pytest.mark.usefixtures("sub_repo_loaded")
def test_filter_not_exist(super_repo_loaded, predicate_foo_bar):
    """Repo returns nothing when elements are filtered out"""
    assert set(super_repo_loaded.filter(predicate_foo_bar)) == set()


@pytest.mark.usefixtures("sub_repo_loaded")
def test_count_exist(super_repo_loaded, predicate_attr_2_sub, predicate_attr_2_super):
    """Repo counts filtered items"""
    assert super_repo_loaded.count(predicate_attr_2_super) == 1
    assert super_repo_loaded.count(predicate_attr_2_sub) == 2
    assert super_repo_loaded.count() == 3


@pytest.mark.usefixtures("sub_repo_loaded")
def test_count_not_exist(super_repo_loaded, predicate_foo_bar):
    """Repo counts 0 items when items are filtered out"""
    assert super_repo_loaded.count(predicate_foo_bar) == 0


def test_pop_not_exists(super_repo_loaded):
    """Repo raises NotFound on popping not existing id"""
    with pytest.raises(super_repo_loaded.NotFound):
        super_repo_loaded.pop('not existing')


def test_remove_exists(super_repo_loaded):
    """Repo removes given object"""
    super_repo_loaded.remove(super_obj)
    assert super_repo_loaded.get_or_none(id_=super_obj.id) is None


def test_remove_not_exists(super_repo_loaded):
    """Repo raises NotFound on removing not existing id"""
    with pytest.raises(super_repo_loaded.NotFound):
        super_repo_loaded.remove(Super(id_='not existing'))


class FooClass(serialization.yaml.YAMLObject):

    yaml_tag = 'foo'
    yaml_constructor = serialization.CustomLoader

    @property
    def id(self):
        return (42, 'foo')


def test_load_from_filepath():
    contents = (
        "---\n"
        "foo: !<foo> {}\n"
    )
    with mock.patch('dharma.utils.serialization.read_from_file') as mocked_read_from_file:
        mocked_read_from_file.return_value = contents
        InMemoryRepository.load_from_filepath('foo.yaml')

    foo_object = serialization.load(contents)['foo']
    assert isinstance(foo_object, FooClass)
