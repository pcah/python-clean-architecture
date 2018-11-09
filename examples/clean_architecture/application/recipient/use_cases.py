import dataclasses
import typing as t

from examples.clean_architecture import application, framework


RecipientId = t.NewType('RecipientId', str)
AccountId = t.NewType('AccountId', str)
AccountNbr = t.NewType('AccountNbr', str)


@dataclasses.dataclass
class CreateNormalInputData:
    recipient_id: RecipientId
    account: AccountNbr


class CreateNormal(framework.UseCase):

    account_service: application.services.AccountService = framework.Inject()
    local_storage: framework.LocalStorage = framework.Inject()

    def process(self, input: framework.UseCaseInput):
        initial_accounts = self.account_service.initial_accounts
        if not initial_accounts:
            raise framework.LogicError
        self.local_storage.store(input.data['id'], 'initial_accounts', initial_accounts)
