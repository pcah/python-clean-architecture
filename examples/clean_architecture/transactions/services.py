from haps import egg, Inject

from . import interfaces


class AccountService:
    """AccountService aka AccountRepo"""
    connector: interfaces.IConnector = Inject()
