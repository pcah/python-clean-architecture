from haps import Inject

from ..services import AccountService


# some framework definitions
class UseCase:
    """
    This is knowledge part of the application. Its methods represent
    application-specific actions that can be taken or queries to ask.
    """


class Resource:
    """
    This is HTTP-specific part of the application. It responses to all
    the `GET`s and `POST`s and knows how to HTML/JSON. It may be CRUD-like
    or respect the Command-Query Responsibility Segregation.
    """
    use_case: UseCase

    def get(self, request):
        pass

    def post(self, request):
        pass


class ValidationError:
    pass


# concrete use case architecture
import dataclasses
import typing as t


RecipientId = t.NewType('RecipientId', str)
AccountId = t.NewType('AccountId', str)
AccountNbr = t.NewType('AccountNbr', str)


@dataclasses.dataclass
class CreateNormalInputData:
    recipient_id: RecipientId
    account: AccountNbr


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
