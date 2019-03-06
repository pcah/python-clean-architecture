from pca.utils.dependency_injection import Component

from . import entities


class InvitationService(Component):

    def is_invitation_valid(self, invitation: entities.Invitation, email: entities.Email):
        return (
            invitation.is_active and
            invitation.email == email and
            invitation.is_inviter_from_same_organization
        )
