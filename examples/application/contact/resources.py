# -*- coding: utf-8 -*-
from examples.framework import pyramid


class CreateRecipientResource(pyramid.PyramidResource):
    """
    Former Flow. No persistent attributes nor states as both are pieces of use-cases.
    """
    use_case_class = CreateRecipient
