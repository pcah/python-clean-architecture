# -*- coding: utf-8 -*-
import dataclasses
import typing as t


RecipientId = t.NewType('RecipientId', str)
AccountId = t.NewType('AccountId', str)
AccountNbr = t.NewType('AccountNbr', str)


@dataclass
class CreateNormalInputData:
    recipient_id: RecipientId
    account: AccountNbr
