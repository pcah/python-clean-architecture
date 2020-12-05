from pca.exceptions import (
    ErrorCatalog,
    QueryError,
)


class QueryErrors(ErrorCatalog):
    NO_FACTORY_DEFINED = QueryError(hint="A repository has no factory defined.")
    UNRESTRICTED_REMOVE = QueryError(
        hint=(
            "A trivial query has been found while doing remove. If you want to clear all the entries "
            "in the dao, use `clear` explicitly."
        )
    )
    CONFLICTING_QUERY_ARGUMENTS = QueryError(
        hint="Arguments used to build the query lead to a contradiction."
    )
    NOT_FOUND = QueryError(hint="The query just didn't find any related entry.")
    IMMUTABLE_DAO = QueryError(hint="This DAO is immutable.")
