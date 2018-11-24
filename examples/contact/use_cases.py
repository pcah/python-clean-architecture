# -*- coding: utf-8 -*-
from examples import framework

from . import schemas


class CreateContact(framework.SimpleUseCase):

    schema_class = schemas.PersonSchema

    contact_repo: examples.application.services.ContactRepo = framework.Inject()
    local_storage: framework.LocalStorage = framework.Inject()

    def action(self, input: framework.UseCaseInput):
        pass
