# -*- coding: utf-8 -*-
from string import ascii_letters

from pca.data import datetime, ip4, string
from pca.domain.entities import Entity

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
