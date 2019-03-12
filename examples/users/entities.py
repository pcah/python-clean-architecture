
"""
Entities are descriptions
"""
import datetime
import typing as t

from examples.framework.domain import Entity, Id
from pca.data.predicate import where


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

    is_active = where('active') == True
    is_deleted = where('active') == False

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

    is_inviter_from_same_organization = where('inviter.organization') == where('organization')
    is_valid_inviter = is_inviter_from_same_organization | where('inviter.is_staff') == True

    @property
    def _today(self):
        return datetime.date.today()

    @property
    def is_active(self):
        return self._today <= self.expires_at
