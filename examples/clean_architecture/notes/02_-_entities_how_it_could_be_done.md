# 2. Data and validation - how it could be done

### Stating the problem

Let's look at this real life example.

```python
class RecipientCreateInputSchema(BaseSchema):
    name = CharField(max_len=40, required=True)
    description = TextField(to_python=lambda value: value.split('\n'))
    destination_account = AccountNrbField(required=True)
    payment_type = ChoiceField(required=True, choices=[
        ('STANDARD', 'STANDARD'),
        ('EXPRESS', 'EXPRESS')
    ])
    currency = CurrencyField(required=False, validators=['validate_currency'])

    def validate_currency(self, value):
        currencies = self.connector.currency_list
        if value not in currencies:
            raise ValidationError(code='BAD-CURRENCY')
```

### A concept
```python
import dataclasses
import enum
import typing as t


AccountNrb = t.NewType('AccountNrb', str)
Currency = t.NewType('Currency', str)


class PaymentType(enum.Enum):
    STANDARD = 'STANDARD'
    EXPRESS = 'EXPRESS'


@dataclasses.dataclass
class RecipientCreateInputData:
    name: str
    description: t.List[str]
    destination_account: AccountNrb
    payment_type: PaymentType
    currency = t.Optional[Currency]
```

First of all, `dataclass` decorator gives the class `__init__` method, based on
variable annotations. One block of boilerplate code less.

Second thought: there's no validation! Any of those `max_length=2`,
`choices=[(1, 'One'), (2, 'Two')]` or `validators=[foo_validator]`. And this is
intentional - dataclass should describe what can be done to a portion
of the data. If some field is described that it is a `str`, you can check if
it starts with a substring or a `List` to iterate through. The validation part
of the Django Form exaple takes place on the boundary of the application layer 
and it is provided by specialised class, the Validator.

```python
class RecipientCreateValidator(Validator):
    pass
```
