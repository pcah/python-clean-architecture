from pca.utils.dependency_injection import (
    Component,
    Container,
    inject,
    Inject,
    scope,
    Scopes,
)


class WheelInterface:
    name: str


class FrameInterface:
    name: str


@scope(Scopes.INSTANCE)
class RoadFrame(FrameInterface):
    name = "Road frame"


class GravelFrame(FrameInterface):
    name = "Gravel frame"


class CustomColoredFrame(FrameInterface):
    def __init__(self, color):
        self.color = color

    @property
    def name(self):
        return f"Custom {self.color} frame"


class RoadWheel(WheelInterface):
    name = "Road wheel"


class GravelWheel(WheelInterface):
    name = "Gravel wheel"


class CustomColoredWheel(WheelInterface):
    def __init__(self, color):
        self.color = color

    @property
    def name(self):
        return f"Custom {self.color} wheel"


class Bike:
    def __init__(self, container: Container):
        """
        Doesn't inherit Component features. Manually uses DI container as a dependency manager and
        sets injected instances to the Bike instance fields.
        """
        self.frame = container.find_by_name("frame")
        self.wheel = container.find_by_interface(WheelInterface)

    @property
    def components(self):
        return {
            "frame": self.frame.name,
            "wheel": self.wheel.name,
        }


class Trike(Component):
    """
    Inherits Component features. Automatically is being injected with DI instances using Inject
    descriptor.
    """

    front_wheel: WheelInterface = Inject()
    left_wheel = Inject(interface=WheelInterface)
    right_wheel = Inject(name="right")
    frame = Inject(name="frame")

    @property
    def components(self):
        return {
            "front_wheel": self.front_wheel.name,
            "left_wheel": self.left_wheel.name,
            "right_wheel": self.right_wheel.name,
            "frame": self.frame.name,
        }

    @inject
    def method_with_dependencies(
        self,
        frame: FrameInterface = Inject(),
        front_wheel=Inject(name="front"),
        rear_wheel=Inject(interface=WheelInterface),
    ):
        pass
