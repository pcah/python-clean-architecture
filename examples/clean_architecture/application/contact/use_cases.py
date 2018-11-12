# -*- coding: utf-8 -*-
from examples.clean_architecture import application, framework

from . import entities


class CreateContact(framework.SimpleUseCase):

    schema_class = CreateContactSchema
    contact_repo: application.services.ContactRepo = framework.Inject()
    local_storage: framework.LocalStorage = framework.Inject()

    def action(self, input: framework.UseCaseInput):
        pass
