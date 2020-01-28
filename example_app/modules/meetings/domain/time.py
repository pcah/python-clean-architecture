import datetime
import typing as t

from pca.domain import ValueObject
from example_app.modules.shared_domain.clock import IClockService
from pca.utils.dependency_injection import inject, Inject


class MeetingTerm(ValueObject):
    start_date: t.Optional[datetime] = None
    end_date: t.Optional[datetime] = None

    @inject
    def is_after_start(self, clock: IClockService = Inject()):
        return clock.now() > self.start_date
