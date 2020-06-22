import pytest

from pca.utils.errors import ExceptionWithCode, ErrorCatalog


class TestCustomError:

    @pytest.fixture
    def instance(self):
        return ExceptionWithCode(code='code', area='area')

    @pytest.fixture
    def instance_with_params(self):
        return ExceptionWithCode(code='code', area='area', params={'foo': 'bar'})

    @pytest.fixture
    def catalog(self):
        return object()

    def test_explicit_arguments(self, instance_with_params: ExceptionWithCode):
        assert instance_with_params.code == 'code'
        assert instance_with_params.area == 'area'
        assert instance_with_params.params == {'foo': 'bar'}
        assert instance_with_params.catalog is None

    def test_defaults(self):
        instance = ExceptionWithCode()
        assert instance.code == ''
        assert instance.area == ''
        assert instance.params is None
        assert instance.catalog is None

    def test_setting_catalog(self, instance: ExceptionWithCode):
        class MyCatalog(ErrorCatalog):
            a = instance

        assert instance.catalog is MyCatalog

    # noinspection PyUnusedLocal
    def test_not_setting_catalog(self, instance: ExceptionWithCode):
        class NotACatalog:
            a = instance

        assert instance.catalog is None

    def test_clone(self, instance_with_params: ExceptionWithCode, catalog):
        instance_with_params.__dict__['catalog'] = catalog
        cloned = instance_with_params.clone()
        assert cloned.code == 'code'
        assert cloned.area == 'area'
        assert cloned.params == {'foo': 'bar'}
        assert cloned.catalog is None
        assert cloned == instance_with_params
        assert cloned is not instance_with_params
        assert cloned.params is not instance_with_params.params

    def test_with_params(self, instance: ExceptionWithCode, catalog):
        instance.__dict__['catalog'] = catalog
        cloned = instance.with_params(a=1)
        assert cloned.code == 'code'
        assert cloned.area == 'area'
        assert cloned.params == {'a': 1}
        assert cloned.catalog is catalog
        assert cloned == instance
        assert cloned is not instance

    def test_equality(self, instance: ExceptionWithCode, catalog):
        cloned = instance.clone()
        instance.__dict__['catalog'] = catalog
        assert instance == cloned
        assert instance != {}
        other_instance = ExceptionWithCode(
            code='code', area='area', params={'different': 'params'})
        assert instance == other_instance
        assert hash(instance) == hash(other_instance)

    def test_equality_while_different_params(
            self,
            instance: ExceptionWithCode,
            instance_with_params: ExceptionWithCode
    ):
        assert instance == instance_with_params
        assert instance.params != instance_with_params.params

    def test_repr(self, instance: ExceptionWithCode, instance_with_params: ExceptionWithCode):
        assert repr(instance) == "ExceptionWithCode(code='code', area='area')"
        assert repr(instance_with_params) == (
            "ExceptionWithCode(code='code', area='area', params={'foo': 'bar'})")

    def test_short_description(
            self,
            instance: ExceptionWithCode,
            instance_with_params: ExceptionWithCode
    ):
        assert instance.short_description == 'area/code'
        assert instance_with_params.short_description == 'area/code/{"foo": "bar"}'


class ExampleCatalog(ErrorCatalog):
    default_area = 'EXAMPLE'

    FOO = ExceptionWithCode()
    BAR = ExceptionWithCode('CODE', 'AREA')


class TestErrorCatalog:

    def test_explicit_arguments(self):
        assert ExampleCatalog.FOO.code == 'FOO'  # based on field name
        assert ExampleCatalog.FOO.area == 'EXAMPLE'  # based on catalog field

    def test_defaults(self):
        assert ExampleCatalog.BAR.code == 'CODE'
        assert ExampleCatalog.BAR.area == 'AREA'

    def test_catalog_ref(self):
        assert ExampleCatalog.FOO.catalog == ExampleCatalog

    def test_in(self):
        assert ExampleCatalog.FOO in ExampleCatalog

    def test_iter(self):
        # noinspection PyTypeChecker
        assert list(ExampleCatalog) == [ExampleCatalog.FOO, ExampleCatalog.BAR]

    def test_all(self):
        assert ExampleCatalog.all() == (
            ExampleCatalog.FOO,
            ExampleCatalog.BAR
        )

    def test_add_instance(self):
        instance = ExceptionWithCode('BAZ')
        ExampleCatalog.add_instance(instance)
        assert instance in ExampleCatalog
        # noinspection PyUnresolvedReferences
        assert ExampleCatalog.BAZ is instance

    def test_same_error_in_multiple_catalogs(self):
        class AnotherCatalog(ErrorCatalog):
            MY = ExampleCatalog.FOO.clone()

        assert AnotherCatalog.MY.catalog == AnotherCatalog
