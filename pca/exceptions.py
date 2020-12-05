import marshmallow.exceptions

from pca.utils.errors import ErrorCatalog  # noqa: F401
from pca.utils.errors import ExceptionWithCode


class BaseError(ExceptionWithCode):
    """
    Base class for all errors that are related to the library (excluding some errors raised by
    `pca.utils`, that are related to purely technical details).
    """


class PcaError(BaseError):
    """
    Base class for all technical errors raised by the very `pca` library
    (and not the domain or application logic). The complementary type is `ProcessError`.
    """


class ConfigError(PcaError):
    """A problem has been encountered during loading configuration of the application."""

    area = "CONFIG"


class IntegrationError(PcaError):
    """A problem has been encountered during loading an integration module."""

    area = "INTEGRATION"


class ProcessError(BaseError):
    """
    A problem with domain or application logic, that happened during executing business process
    (contrary to technical problems, described by the complementary type: `PcaError`).
    """


class QueryError(ProcessError):
    """Process errors that are related to processing queries."""

    area = "QUERY"


class ValidationError(ProcessError, marshmallow.exceptions.ValidationError):
    """
    Process errors that happened during the data validation step of business logic.
    # TODO #39. integrate validation
    """

    area = "VALIDATION"


class LogicError(ProcessError):
    """
    Base error class for errors of purely business logic. This is the main
    """

    area = "LOGIC"
