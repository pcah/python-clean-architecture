import pytest

from pca.exceptions import ConfigError
from pca.utils.dependency_injection import (
    Component,
    DIContext,
    DIErrors,
    get_scope_type,
    scope,
    Scopes,
)

from .common import (
    Bike,
    CustomColoredFrame,
    CustomColoredWheel,
    FrameInterface,
    GravelFrame,
    RoadFrame,
    RoadWheel,
    WheelInterface,
)


class TestContainer:
    def test_container_registration_(self, container):
        container.register_by_name(name='frame', constructor=RoadFrame)
        container.register_by_interface(interface=WheelInterface, constructor=RoadWheel)
        assert Bike(container).components == {
            'frame': 'Road frame',
            'wheel': 'Road wheel',
        }

    def test_container_interface_duplicates(self, container):
        interface = FrameInterface
        container.register_by_interface(interface, RoadFrame)
        # registering again the same signature results with an error
        with pytest.raises(ConfigError) as error_info:
            container.register_by_interface(interface, GravelFrame)
        assert error_info.value == DIErrors.AMBIGUOUS_DEFINITION
        assert error_info.value.params == {'context': DIContext(interface=FrameInterface)}
        # but registering with the same interface and different qualifier is a different signature
        # and ends with a success
        container.register_by_interface(interface, GravelFrame, qualifier='gravel')

    def test_container_interface_not_found(self, container):
        interface = FrameInterface
        qualifier = 'qualifier'
        with pytest.raises(ConfigError) as error_info:
            container.find_by_interface(interface, qualifier)
        assert error_info.value == DIErrors.DEFINITION_NOT_FOUND
        assert error_info.value.params == {
            'context': DIContext(interface=FrameInterface, qualifier='qualifier')}

    def test_container_name_duplicates(self, container):
        name = 'frame'
        container.register_by_name(name=name, constructor=RoadFrame)
        # registering again the same signature results with an error
        with pytest.raises(ConfigError) as error_info:
            container.register_by_name(name=name, constructor=GravelFrame)
        assert error_info.value == DIErrors.AMBIGUOUS_DEFINITION
        assert error_info.value.params == {'context': DIContext(name='frame')}
        # but registering with the same interface and different qualifier is a different signature
        # and ends with a success
        container.register_by_name(name=name, constructor=GravelFrame, qualifier='gravel')

    def test_container_name_not_found(self, container):
        name = 'frame'
        qualifier = 'qualifier'
        with pytest.raises(ConfigError) as error_info:
            container.find_by_name(name, qualifier)
        assert error_info.value == DIErrors.DEFINITION_NOT_FOUND
        assert error_info.value.params == {
            'context': DIContext(name='frame', qualifier='qualifier')}

    def test_constructor_kwargs(self, container):
        container.register_by_name(
            name='frame',
            constructor=CustomColoredFrame,
            kwargs={'color': 'pink'}
        )
        container.register_by_interface(
            interface=WheelInterface,
            constructor=CustomColoredWheel,
            kwargs={'color': 'pink'}
        )
        assert Bike(container).components == {
            'frame': 'Custom pink frame',
            'wheel': 'Custom pink wheel'
        }


class TestScopes:

    def test_scope_class(self, container):
        assert repr(Scopes.INSTANCE) == f'<Scopes.{Scopes.INSTANCE.name}>'
        assert Scopes.INSTANCE(container, RoadWheel, {}).name == 'Road wheel'

    def test_scope_decorator(self, container):
        @scope(Scopes.SINGLETON)
        class MyFrame(FrameInterface, Component):
            name = 'My frame'

        container.register_by_name(name='frame', constructor=MyFrame)
        instance_1 = container.find_by_name('frame')
        instance_2 = container.find_by_name('frame')
        assert get_scope_type(MyFrame) is Scopes.SINGLETON
        assert instance_1 is instance_2

    def test_singleton_scope(self, container):
        container.register_by_name(name='frame', constructor=RoadFrame, scope=Scopes.SINGLETON)
        instance_1 = container.find_by_name('frame')
        instance_2 = container.find_by_name('frame')
        assert instance_1 is instance_2
