# -*- coding: utf-8 -*-
from examples.clean_architecture import application, framework


class CreateRecipient(framework.UseCase):

    account_service: application.services.AccountService = framework.Inject()
    local_storage: framework.LocalStorage = framework.Inject()

    def perform(self, input: framework.UseCaseInput):
        initial_accounts = self.account_service.initial_accounts
        if not initial_accounts:
            raise framework.LogicError
        self.local_storage.store(input.data['id'], 'initial_accounts', initial_accounts)
