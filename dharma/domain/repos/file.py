# -*- coding: utf-8 -*-
from .in_memory import InMemoryRepository


class FileRepository(InMemoryRepository):

    def __init__(self, klass, filepath=None):
        super(FileRepository, self).__init__(klass)
        if filepath:
            self.load(filepath)

    def load(self, filepath):
        pass
