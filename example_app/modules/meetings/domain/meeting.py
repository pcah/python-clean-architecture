from pca.domain import Entity, Id, ValueObject

from .time import MeetingTerm


class Meeting(Entity):
    id = Id()

    title: str
    term: MeetingTerm
    description: str
