"""
Some common interfaces and services.
"""
from pca.utils.dependency_injection import Component


class IRequest:
    """
    Interface for a facade which represents a request. Largely depends on a concrete
    implementation.
    """


class ISession:
    """
    Interface for a session (whatever that means for your application) and its local storage.
    """


class IUser:
    """Base interface for a user entity."""


class AuthenticationService(Component):
    user: IUser
    # TODO some implementation of how user instances are acquired
