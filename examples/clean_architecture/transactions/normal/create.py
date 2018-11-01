from haps import Inject

from ..services import AccountService


# some framework definitions
class UseCase:
    pass


class Resource:

    def __getattr__(self, action='init'):
        return getattr(self.use_case, action)


class ValidationError:
    pass


# concrete use case architecture
import dataclasses
import typing as t


RecipientId = t.NewType('RecipientId', str)
AccountId = t.NewType('AccountId', str)
AccountNrb = t.NewType('AccountNrb', str)


@dataclasses.dataclass
class CreateNormalInputData:
    recipient_id: RecipientId
    account: AccountNrb


class CreateNormal(UseCase):

    account_service: AccountService = Inject()
    iss_repo: AccountService = Inject()

    def init(self, id_, **data):
        initial_accounts = self.account_service.initial_accounts
        if not initial_accounts:
            raise ValidationError
        self.iss_repo.store(id_, 'initial_accounts', initial_accounts)


class CreateNormalResource(Resource):
    """
    Former Flow. No persistent attributes nor states as both are pieces of use-cases.
    """
    use_case = CreateNormal()
