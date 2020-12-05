import datetime
import typing as t

from meetapp.modules.shared_domain.clock import IClockService

from pca.domain import ValueObject
from pca.utils.dependency_injection import (
    Inject,
    inject,
)


class MeetingTerm(ValueObject):
    start_date: t.Optional[datetime] = None
    end_date: t.Optional[datetime] = None

    @inject
    def is_after_start(self, clock: IClockService = Inject()):
        return clock.now() > self.start_date
