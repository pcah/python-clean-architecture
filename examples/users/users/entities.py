# -*- coding: utf-8 -*-
from string import ascii_letters

from dharma.data import datetime, ip4, string
from dharma.domain.entities import Entity

from . import validation


class User(Entity):
    login = string(required=True, min_len=6, max_len=16, chars=ascii_letters)
    first_name = string()
    last_name = string()
    password = string(
        required=True, min_len=6, max_len=32, chars=validation.CHARS,
        validators=[
            validation.validate_different_characters,
            validation.validate_special_chars
    ]   )  # encrypted

    last_login = datetime(required=True)
    ip = ip4(required=True)
