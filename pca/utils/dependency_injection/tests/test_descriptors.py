import pytest

from pca.exceptions import ConfigError
from pca.utils.dependency_injection import (
    Component,
    DIErrors,
    create_component,
    get_attribute_dependencies,
    Inject,
)

from .common import (
    FrameInterface,
    GravelFrame,
    GravelWheel,
    RoadFrame,
    RoadWheel,
    WheelInterface,
    Trike,
)


class TestInjectDescriptor:
    @pytest.fixture
    def container(self, container):
        container.register_by_interface(FrameInterface, RoadFrame)
        container.register_by_interface(WheelInterface, RoadWheel)
        container.register_by_name('frame', GravelFrame)
        container.register_by_name('wheels', RoadWheel)
        container.register_by_name('right', GravelWheel)
        container.register_by_name('instance', Trike)
        return container

    @pytest.fixture
    def instance(self, container):
        return container.find_by_name('instance')

    def test_descriptor_injection(self, instance):
        assert instance.components == {
            'front_wheel': 'Road wheel',
            'left_wheel': 'Road wheel',
            'right_wheel': 'Gravel wheel',
            'frame': 'Gravel frame',
        }

    def test_get_class(self):
        class Bike(Component):
            wheel: WheelInterface = Inject()

        assert isinstance(Bike.wheel, Inject)

    def test_no_name_no_interface(self, container):
        class NoAnnotationBike(Component):
            wheel = Inject()

        instance = create_component(NoAnnotationBike, container)
        with pytest.raises(ConfigError) as error_info:
            assert instance.wheel
        assert error_info.value == DIErrors.NO_IDENTIFIER_SPECIFIED
        assert error_info.value.params == {
            'class_name': (
                'TestInjectDescriptor.test_no_name_no_interface.'
                '<locals>.NoAnnotationBike'
            ),
            'attribute': 'wheel',
        }

    def test_no_container(self, container):
        class A:
            descriptor = Inject()
        with pytest.raises(ConfigError) as error_info:
            assert A().descriptor
        assert error_info.value == DIErrors.NO_CONTAINER_PROVIDED.with_params(
            module='', attribute='descriptor')
        assert error_info.value.params == {
            'class_name': 'TestInjectDescriptor.test_no_container.<locals>.A',
            'attribute': 'descriptor'
        }

    def test_get_dependencies_successful(self, instance):
        dependencies = get_attribute_dependencies(instance)
        assert {k: v.name for k, v in dependencies.items()} == instance.components

    def test_get_dependencies_no_description(self):
        # instance is an non-DI-aware object
        instance = object()
        assert get_attribute_dependencies(instance) == {}
