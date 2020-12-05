[[⬅ Back to ToC](../README.md)]

# 2. Data and validation - how it could be done

### A concept
```python
import dataclasses
import enum
import typing as t


AccountNbr = t.NewType('AccountNbr', str)
Currency = t.NewType('Currency', str)


class PaymentType(enum.Enum):
    STANDARD = 'STANDARD'
    EXPRESS = 'EXPRESS'


@dataclasses.dataclass
class RecipientCreateInputData:
    name: str
    description: t.List[str]
    destination_account: AccountNbr
    payment_type: PaymentType
    currency = t.Optional[Currency]
```

First of all, `dataclass` decorator gives the class `__init__` method, based on
variable annotations. One block of boilerplate code less.

Second observation: variable annotations with types gives you typing check
through type hinting feature (using [mypy](http://mypy-lang.org/) or your IDE
code introspection).

Third observation: there's no validation! Any of those `max_length=2`,
`choices=[(1, 'One'), (2, 'Two')]` or `validators=[foo_validator]`. And this is
intentional - dataclass should describe what can be done to a portion
of the data. If some field is described that it is a `str`, you can check if
If it's a list `List` —  to iterate through. The validation part
of the Django Form example takes place on the boundary of the application layer
and it is provided by specialised class, the Validator.

```python
class RecipientCreateValidator(Validator):
    dataclass = RecipientCreateInputData
    name = {'max_len': 40, charset=}
```
