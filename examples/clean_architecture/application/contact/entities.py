# -*- coding: utf-8 -*-
from dataclasses import dataclass
from enum import Enum
import typing as t


Email = t.NewType('Email', str)
Phone = t.NewType('Phone', str)


class Position(Enum):
    UNKNOWN = None


@dataclass
class Company:
    name: str
    address: t.Optional[str] = None
    contact_email: t.Optional[Email] = None


@dataclass
class Person:
    first_name: str
    last_name: str
    email: t.Optional[Email] = None
    phone: t.Optional[Phone] = None
    company: t.Optional[Company] = None
    position: t.Optional[Position] = None


@dataclass
class CreateContactInput:
    is_company: bool
    data: t.Union[Person, Company]
