# -*- coding: utf-8 -*-
from . import entities


def is_invitation_valid(invitation: entities.Invitation, email: entities.Email):
    return (
        invitation.is_active and
        invitation.email == email and
        invitation.is_inviter_from_same_organization
    )
