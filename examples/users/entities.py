"""
Entities are representations of business logic objects that have some distinctive identity.
"""
import datetime
import typing as t

from pca.data.predicate import where
from pca.domain.entity import Entity

from examples.framework_ideas.domain import Id
from examples.framework_ideas.logic_programming import PredicateDescriptor


# ValueObject
Email = t.NewType('Email', str)
InvitationToken = t.NewType('InvitationToken', str)


class Organization(Entity):
    id: Id('name')
    name: str
    email: Email
    user_limit: int


class User(Entity):
    id: Id
    first_name: str
    last_name: str
    email: Email
    organization: t.List[Organization]
    is_staff: bool  # has additional privileges to invite

    is_active = PredicateDescriptor(where('active') == True)  # noqa: E712
    is_deleted = PredicateDescriptor(where('active') == False)  # noqa: E712

    @property
    def full_name(self):
        return f"{self.first_name} f{self.last_name}"


class Invitation(Entity):
    id: Id('email', 'organization')
    token: InvitationToken
    email: Email
    inviter: User
    organization: Organization
    sent_at: datetime.datetime
    expires_at: datetime.date

    is_inviter_from_same_organization = PredicateDescriptor(
        where('inviter.organization') == where('organization'))
    is_valid_inviter = PredicateDescriptor(
        is_inviter_from_same_organization | where('inviter.is_staff') == True  # noqa: E712
    )

    @property
    def _today(self):
        return datetime.date.today()

    @property
    def is_active(self):
        return self._today <= self.expires_at

    def accept(self):
        raise NotImplementedError
