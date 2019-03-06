from pca.application.interactor import RequestModel, ResponseModel
from pca.utils.dependency_injection import Inject

from examples.application import BaseInteractor, application

from . import (
    repositories,
    validators
)


@application.controller('users/invite')
class InviteUser(BaseInteractor):

    user_repo: repositories.UserRepo = Inject()
    invitation_repo: repositories.InvitationRepo = Inject()

    @property
    def validators(self):
        return (self.validate_email_taken,)

    def validate_email_taken(self, request, dependencies):
        self.user_repo.is_email_taken(request['email'])

    def execute(self, request: RequestModel) -> ResponseModel:
        invitation = self.invitation_repo.create_and_add(email=request['email'])
        return ResponseModel(data=self.invitation_repo.serialize(invitation), errors={})


@application.controller('users/accept')
class AcceptInvitation(BaseInteractor):

    user_repo: repositories.UserRepo = Inject()
    invitation_repo: repositories.InvitationRepo = Inject()

    validators = (
        validators.is_invitation_valid,
        validators.is_email_taken,
    )

    def execute(self, request: RequestModel) -> ResponseModel:
        invitation = self.invitation_repo.get_by_token(request['token'])
        data = invitation.accept()
        return ResponseModel(data=data, errors={})
