# -*- coding: utf-8 -*-
from pca.data.formulae import where

from examples.framework.repo import AbstractRepo
from examples.framework.integrations.common import IDao, ISession
from examples.framework.dependency_injection import Inject

from . import entities


class UserRepo(AbstractRepo):
    dao: IDao = Inject(qualifier=entities.User)
    session: ISession = Inject()

    is_active = where('active') == True
    is_deleted = where('active') == False

    @property
    def is_from_my_organization(self):
        organization = self.session.user.organization
        return where('organization.id') == organization.id

    def get_by_email(self, email):
        data = self.dao.get(
            where('email') == email &
            entities.User.is_active &
            self.is_from_my_organization
        )
        return entities.User(**data)

    def is_email_taken(self, email):
        return self.dao.exists(where('email') == email)


class InvitationRepo(AbstractRepo):
    dao: IDao = Inject(qualifier=entities.Invitation)
    session: ISession = Inject()

    q_inviter_from_same_organization = where('inviter.organization') == where('organization')
    q_valid_inviter = q_inviter_from_same_organization | where('inviter.is_staff') == True

    def get_by_email(self, email: entities.Email, organization: entities.Organization):
        data = self.dao.get(
            (where('email') == email) &
            (where('organization') == organization)
        )
        return entities.Invitation(**data)

    def get_by_token(self, token: entities.InvitationToken):
        data = self.dao.get(where('token') == token)
        return entities.Invitation(**data)
