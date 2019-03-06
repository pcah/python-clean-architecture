from pca.application.interactor import RequestModel
from pca.exceptions import ErrorCatalog, LogicError

from examples.users.repositories import InvitationRepo, UserRepo


class InvitingErrors(ErrorCatalog):
    INVITATION_EXPIRED = LogicError()
    EMAIL_TAKEN = LogicError()


def is_invitation_valid(request: RequestModel, invitation_repo: InvitationRepo, **kwargs):
    raise InvitingErrors.INVITATION_EXPIRED


def is_email_taken(request: RequestModel, user_repo: UserRepo, **kwargs):
    email = request['email']
    if user_repo.is_email_taken(email):
        raise InvitingErrors.EMAIL_TAKEN.with_params(email=email)
