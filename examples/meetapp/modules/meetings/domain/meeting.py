from pca.domain import (  # noqa: F401
    Entity,
    Uuid4Id,
    ValueObject,
)

from .time import MeetingTerm


class Meeting(Entity):
    id = Uuid4Id()
    title: str
    term: MeetingTerm
    description: str
