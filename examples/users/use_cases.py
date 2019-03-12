from examples.framework.use_case import (
    UseCase,
    UseCaseInput,
)
from pca.utils.dependency_injection import Inject

from . import entities, repos, services


class InvitateUserInput(UseCaseInput):
    email: entities.Email


class InvitateUser(UseCase):

    input_class = InvitateUserInput

    def is_available(self, data: InvitateUserInput):
        user_repo = repos.UserRepo(self.container)
        return not user_repo.is_email_taken(data.email)


class AcceptInvitation(UseCase):

    user_repo: repos.UserRepo = Inject()
    invitation_repo: repos.InvitationRepo = Inject()

    class Input(UseCaseInput):
        email: entities.Email
        token: entities.InvitationToken

    def is_available(self, data: Input):
        invitation = self.invitation_repo.get_by_token(data.token)
        return (
            not self.user_repo.is_email_taken(data.email) and
            services.is_invitation_valid(invitation, data.email)
        )
