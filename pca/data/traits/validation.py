# -*- coding: utf-8 -*-
import re

from pca.exceptions import TraitValidationError


def construct_validators(genus):
    return ()


EMAIL_USER_RE = re.compile(
    # dot-atom
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"
    # quoted-string
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',
    re.IGNORECASE
)
EMAIL_DOMAIN_RE = re.compile(
    # max length for domain name labels is 63 characters per RFC 1034
    r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z',
    re.IGNORECASE)
EMAIL_LITERAL_RE = re.compile(
    # literal form, ipv4 or ipv6 address (SMTP 4.1.3)
    r'\[([A-f0-9:\.]+)\]\Z',
    re.IGNORECASE)


def validate_domain_part(value):
    pass


def validate_email(value, whitelist):
    if not value or '@' not in value:
        raise TraitValidationError(code='MALFORMED_EMAIL')

    user_part, domain_part = value.rsplit('@', 1)

    if not EMAIL_USER_RE.match(user_part):
        raise TraitValidationError(code='MALFORMED_EMAIL')

    if (domain_part not in whitelist and
            not validate_domain_part(domain_part)):
        # Try for possible IDN domain-part
        try:
            domain_part = domain_part.encode('idna').decode('ascii')
            if validate_domain_part(domain_part):
                return
        except UnicodeError:
            pass
        raise TraitValidationError(code='MALFORMED_EMAIL')


IPv4_RE = re.compile(
    r'^(?:(?:2[0-4]\d|25[0-5]|1\d{2}|[1-9]?\d)\.){3}(?:2[0-4]\d|25[0-5]|1\d{2}|[1-9]?\d)$')
