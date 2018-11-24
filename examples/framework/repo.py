# -*- coding: utf-8 -*-
from .dependency_injection import Container
from .integrations.common import IDao


class AbstractRepo:

    dao: IDao

    def __init__(self, container: Container):
        self.container = container
