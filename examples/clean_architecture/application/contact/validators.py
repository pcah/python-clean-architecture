# -*- coding: utf-8 -*-
import re


def validate_phone(value):
    return bool(re.match(r'^[1-9]{9}$', value))
