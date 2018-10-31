from haps import Inject

from ..services import AccountService


# some framework definitions
class UseCase:
    pass


class Resource:
    pass


class ValidationError:
    pass


# concrete use case architecture
class CreateNormalResource(Resource):
    """
    Former Flow. No persistent attributes nor states as both are pieces of use-cases.
    """
    @property
    def use_case(self):
        return CreateNormal()

    def __getattr__(self, action='init'):
        return getattr(self.use_case, action)


class CreateNormal(UseCase):

    account_service: AccountService = Inject()
    iss_repo: AccountService = Inject()

    def init(self, id_, **data):
        initial_accounts = self.account_service.initial_accounts
        if not initial_accounts:
            raise ValidationError
        self.iss_repo.store(id_, 'initial_accounts', initial_accounts)
