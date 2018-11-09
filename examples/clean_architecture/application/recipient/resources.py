# -*- coding: utf-8 -*-
from examples.clean_architecture.framework import pyramid

from .use_cases import *


class CreateNormalResource(pyramid.PyramidResource):
    """
    Former Flow. No persistent attributes nor states as both are pieces of use-cases.
    """
    use_case = CreateNormal
