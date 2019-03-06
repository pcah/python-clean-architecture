from pca.data.predicate import where
from pca.domain.repository import Repository, Schema
from pca.utils.dependency_injection import Inject

from ..framework_ideas.integrations.common import AuthenticationService
from . import entities


class UserRepo(Repository):
    schema: Schema = Schema(entity=entities.User)

    authentication: AuthenticationService = Inject()

    @property
    def is_from_my_organization(self):
        organization = self.authentication.user.organization
        return where('organization.id') == organization.id

    def get_by_email(self, email):
        data = self.dao.filter(
            where('email') == email &
            entities.User.is_active &
            self.is_from_my_organization
        ).one()
        return self.create(**data)

    def is_email_taken(self, email):
        return self.dao.filter(where('email') == email).exists()


class InvitationRepo(Repository):
    schema: Schema = Schema(entity=entities.Invitation)

    q_inviter_from_same_organization = where('inviter.organization') == where('organization')
    q_valid_inviter = q_inviter_from_same_organization | \
                      where('inviter.is_staff') == True  # noqa: E712

    def get_by_email(self, email: entities.Email, organization: entities.Organization):
        data = self.dao.filter(
            (where('email') == email) &
            (where('organization') == organization)
        ).one()
        return self.create(**data)

    def get_by_token(self, token: entities.InvitationToken):
        data = self.dao.filter(where('token') == token).one()
        return self.create(**data)
