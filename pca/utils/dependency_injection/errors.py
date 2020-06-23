from pca.exceptions import ConfigError, ErrorCatalog


class DIErrors(ErrorCatalog):
    DEFINITION_NOT_FOUND = ConfigError(hint=(
        "A dependency definition for DI was tried to be injected, but it has not been found."
    ))
    ALREADY_REGISTERED = ConfigError(hint="This context has already been registered.")
    AMBIGUOUS_DEFINITION = ConfigError(hint=(
        "A dependency definition must have exactly only one of the two: either the name "
        "or the interface."
    ))
    NO_IDENTIFIER_SPECIFIED = ConfigError(hint="Missing both name and interface for Inject.")
    CONTRADICTORY_QUALIFIER_DEFINED = ConfigError(hint=(
        "Both `qualifier` value and `get_qualifier` factory should not be set on the same "
        "DI context. Choose one."
    ))
    INDETERMINATE_CONTEXT_BEING_RESOLVED = ConfigError(hint=(
        "The context has to be determined (i.e. called `determine(component)`) to be resolvable."
    ))
    NO_CONTAINER_PROVIDED = ConfigError(
        hint="DI resolving found no instance of the DI `Container` to work with.")
