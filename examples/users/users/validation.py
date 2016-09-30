# -*- coding: utf-8 -*-
import string

from dharma.exceptions import TraitValidationError


CHARS = string.ascii_letters
SPECIAL_PASSWORD_CHARS = '!@#$%^&*()[]{};\':",./<>?\\|~`'


def validate_special_chars(value):
    if not any(c in value for c in SPECIAL_PASSWORD_CHARS):
        raise TraitValidationError(code='CHAR_NOT_ALLOWED')


def validate_different_characters(value):
    if len(set(value)) < 5:
        raise TraitValidationError(code='NOT_ENOUGH_DIFFERENT_CHARS')
