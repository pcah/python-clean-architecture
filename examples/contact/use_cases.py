from examples import framework

from . import schemas, repos


class CreateContact(framework.SimpleUseCase):

    schema_class = schemas.PersonSchema

    contact_repo: repos.ContactRepo = framework.Inject()
    local_storage: framework.LocalStorage = framework.Inject()

    def action(self, input: framework.UseCaseInput):
        pass
