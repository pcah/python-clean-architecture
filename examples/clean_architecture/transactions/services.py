from haps import egg, Inject

from . import interfaces
from . import models

class AccountService:
    """AccountService aka AccountRepo"""
    connector: interfaces.IConnector = Inject()

    def initial_accounts(self) -> models.Account:
        return
