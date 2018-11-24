# -*- coding: utf-8 -*-
from marshmallow import fields
from marshmallow_annotations import (
    AnnotationSchema,
    registry,
)

from . import (
    entities,
    validators,
)


TYPES_TO_REGISTER_AS_FIELDS = {
    entities.Email: fields.Email,
    entities.Phone: fields.Str(
        validate=validators.validate_phone
    ),
}
for type_, field in TYPES_TO_REGISTER_AS_FIELDS.items():
    registry.register_field_for_type(type_, field)


class CompanySchema(AnnotationSchema):
    class Meta:
        target = entities.Company
        register_as_scheme = True


class PersonSchema(AnnotationSchema):
    class Meta:
        target = entities.Person
        register_as_scheme = True
