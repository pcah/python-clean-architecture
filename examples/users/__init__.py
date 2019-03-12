from examples.dependency_injection import container
from examples.framework.integrations import common, django

from . import entities


container.register_by_interface(
    interface=common.IDao, qualifier=entities.User, constructor=django.DjangoDao)
container.register_by_interface(
    interface=common.IDao, qualifier=entities.Organization, constructor=django.DjangoDao)
