from pca.exceptions import (
    ConfigError,
    ErrorCatalog,
    IntegrationError,
)


class IntegrationErrors(ErrorCatalog):
    NOT_FOUND = IntegrationError(hint="A library, that should be integrated, hasn't been found.")
    NO_TABLE_NAME_PROVIDED = ConfigError(
        hint="A DB's table name, for integration with a DB library, hasn't been provided."
    )
