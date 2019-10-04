from pca.exceptions import ConfigError, ErrorCatalog


class DIErrors(ErrorCatalog):
    DEFINITION_NOT_FOUND = ConfigError(hint=(
        "A dependency definition for DI was tried to be injected, but it has not been found."))
    AMBIGUOUS_DEFINITION = ConfigError(hint="This identifier has already been registered.")
    NO_IDENTIFIER_SPECIFIED = ConfigError(hint="Missing both name and interface for Inject.")
    NO_CONTAINER_PROVIDED = ConfigError(
        hint="DI resolving found no instance of the DI `Container` to work with.")
    INTEGRATION_NOT_FOUND = ConfigError(hint=(
        "An integration target tried to use its external library, but it has not been found."))
