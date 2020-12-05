import abc

from datetime import (
    datetime,
    timedelta,
    tzinfo,
)


class IClockService(abc.ABC):
    """Abstract interface of common clock service."""

    @property
    @abc.abstractmethod
    def timezone(self) -> tzinfo:
        """Returns timezone of the clock."""

    @abc.abstractmethod
    def now(self) -> datetime:
        """Returns timezone-aware `now` datetime of the clock."""


class ISettableClockService(IClockService):
    """Abstract interface of clock service, which has settable `now`."""

    @abc.abstractmethod
    def set(self, now: datetime) -> None:
        """Sets `now` of the clock."""

    @abc.abstractmethod
    def tick(self, delta: timedelta) -> None:
        """Advances `now` of the clock."""


class SystemClockService(IClockService):
    """Clock service implemented using stdlib `datetime`."""

    _timezone: tzinfo

    def __init__(self, timezone: tzinfo):
        self._timezone = timezone

    @property
    def timezone(self) -> tzinfo:
        return self._timezone

    def now(self) -> datetime:
        return datetime.now(self._timezone)


class MockClockService(ISettableClockService):
    """Clock service implementing a static clock. It advances its time only manually."""

    _preset_now: datetime

    def __init__(self, now: datetime):
        """`now` is expected to be already timezone-aware."""
        self._preset_now = now

    @property
    def timezone(self) -> tzinfo:
        return self._preset_now.tzinfo

    def now(self) -> datetime:
        return self._preset_now

    def set(self, now: datetime) -> None:
        self._preset_now = now

    def tick(self, delta: timedelta) -> None:
        self._preset_now += timedelta
