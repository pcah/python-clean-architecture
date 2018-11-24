# -*- coding: utf-8 -*-
from examples.dependency_injection import container
from examples.framework.integrations import common, django, in_memory

from . import entities


container.register_by_interface(
    interface=common.IDao, qualifier=entities.User, constructor=django.DjangoDao)
container.register_by_interface(
    interface=common.IDao, qualifier=entities.Organization, constructor=in_memory.InMemoryDai)
