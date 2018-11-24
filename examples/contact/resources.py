# -*- coding: utf-8 -*-
from examples.framework.integrations import pyramid


class CreateRecipientResource(pyramid.PyramidResource):
    """
    Former Flow. No persistent attributes nor states as both are pieces of use-cases.
    """
    use_case_class = CreateRecipient
