from pca.domain import Entity, Uuid4Id, ValueObject  # noqa: F401

from .time import MeetingTerm


class Meeting(Entity):
    id = Uuid4Id()
    title: str
    term: MeetingTerm
    description: str
