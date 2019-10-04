import mock
import pytest

from pca.exceptions import ConfigError
from pca.utils.dependency_injection import (
    Component,
    DIContext,
    DIErrors,
    container_supplier,
    create_component,
    inject,
    Inject,
)

from .common import (
    FrameInterface,
    GravelFrame,
    GravelWheel,
    RoadFrame,
    RoadWheel,
    WheelInterface,
)


class TestInjectDecorator:

    class Bike(Component):

        @inject
        def construct_successfully(
                self,
                frame: FrameInterface = Inject(),
                front_wheel=Inject(name='front'),
                rear_wheel=Inject(interface=WheelInterface)
        ):
            # noinspection PyDataclass
            return {
                'frame': frame.name,
                'front': front_wheel.name,
                'rear': rear_wheel.name
            }

        @inject
        def construct_without_identifier(self, frame=Inject()):
            pass

    @pytest.fixture
    def container(self, container):
        container.register_by_interface(FrameInterface, RoadFrame)
        container.register_by_interface(WheelInterface, RoadWheel)
        container.register_by_name('front', GravelWheel)
        return container

    @pytest.fixture
    def context(self):
        """An empty DI context"""
        return DIContext()

    @pytest.fixture
    def instance(self, container, context):
        return create_component(self.Bike, container, context)

    def test_inject(self, instance):
        assert instance.construct_successfully() == {
            'frame': 'Road frame',
            'front': 'Gravel wheel',
            'rear': 'Road wheel',
        }

    def test_inject_args(self, container, instance):
        with pytest.raises(TypeError) as error_info:
            instance.construct_successfully(GravelFrame())
        assert str(error_info.value) == \
            "construct_successfully() got multiple values for argument 'frame'"

    def test_inject_kwargs(self, container, instance):
        assert instance.construct_successfully(frame=GravelFrame()) == {
            'frame': 'Gravel frame',
            'front': 'Gravel wheel',
            'rear': 'Road wheel',
        }

    def test_inject_no_name_or_interface(self, instance):
        with pytest.raises(ConfigError) as error_info:
            instance.construct_without_identifier()
        assert error_info.value == DIErrors.NO_IDENTIFIER_SPECIFIED

    def test_inject_no_container(self):
        instance = self.Bike()
        with pytest.raises(ConfigError) as error_info:
            assert instance.construct_successfully()
        assert error_info.value == DIErrors.NO_CONTAINER_PROVIDED

    def test_injectable_function(self, container, context):
        mock_dependency = mock.Mock()
        container.register_by_name("dependency", lambda *args: mock_dependency)

        @container_supplier
        @inject
        def f(dependency=Inject(name="dependency"), **kwargs):
            # noinspection PyCallingNonCallable
            dependency(**kwargs)
            return 42

        f_closure = f(container, context)
        result = f_closure(foo='bar')

        mock_dependency.assert_called_once_with(foo='bar')
        assert result == 42
