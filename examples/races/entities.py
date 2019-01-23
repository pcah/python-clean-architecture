from pca.domain.entity import Entity


class Team(Entity):
    name: str


class Racer(Entity):
    first_name: str
    last_name: str


class RaceCourse(Entity):
    name: str


# TODO: ValueObject
class Race(Entity):
    course: RaceCourse
    year: int
