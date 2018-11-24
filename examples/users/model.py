# -*- coding: utf-8 -*-
"""
Integration point with Django framework. It expects application DAOs
(named Models) to be placed in `models` module in the package directory.

PCA helps you auto-generate these models from the entity description, but you
can take control of details of the auto-generation process or build them by
hand and only verify compatibility with the entities.
"""
from examples.framework.integrations.django import django_model_factory

from examples.users import entities


UserModel = django_model_factory(entities.User)
InvitationModel = django_model_factory(entities.Invitation)
