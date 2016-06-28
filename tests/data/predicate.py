import pytest

from dharma.data.formulae.predicate import Var, where


def test_no_path():
    with pytest.raises(ValueError):
        Var() == 2


def test_orm_like_usage():
    data = {'name': 'John', 'age': {'year': 2000}}

    User = Var()
    predicate1 = User.name == 'John'
    predicate2 = User.age.year == 2000
    assert predicate1(data)
    assert predicate2(data)


def test_sql_like_usage():
    data = {'name': 'John', 'age': {'year': 2000}}

    predicate1 = where('name') == 'John'
    predicate2 = where('age.year') == 2000
    assert predicate1(data)
    assert predicate2(data)


def test_eq():
    predicate = Var().value == 1
    assert predicate({'value': 1})
    assert not predicate({'value': 2})
    assert hash(predicate)

    predicate = Var().value == [0, 1]
    assert predicate({'value': [0, 1]})
    assert not predicate({'value': [0, 1, 2]})
    assert hash(predicate)


def test_ne():
    predicate = Var().value != 1
    assert predicate({'value': 2})
    assert not predicate({'value': 1})
    assert hash(predicate)

    predicate = Var().value != [0, 1]
    assert predicate({'value': [0, 1, 2]})
    assert not predicate({'value': [0, 1]})
    assert hash(predicate)


def test_lt():
    predicate = Var().value < 1
    assert predicate({'value': 0})
    assert not predicate({'value': 1})
    assert hash(predicate)


def test_le():
    predicate = Var().value <= 1
    assert predicate({'value': 0})
    assert predicate({'value': 1})
    assert not predicate({'value': 2})
    assert hash(predicate)


def test_gt():
    predicate = Var().value > 1
    assert predicate({'value': 2})
    assert not predicate({'value': 1})
    assert hash(predicate)


def test_ge():
    predicate = Var().value >= 1
    assert predicate({'value': 2})
    assert predicate({'value': 1})
    assert not predicate({'value': 0})
    assert hash(predicate)


def test_or():
    predicate = (
        (Var().val1 == 1) |
        (Var().val2 == 2)
    )
    assert predicate({'val1': 1})
    assert predicate({'val2': 2})
    assert predicate({'val1': 1, 'val2': 2})
    assert not predicate({'val1': '', 'val2': ''})
    assert hash(predicate)


def test_and():
    predicate = (
        (Var().val1 == 1) &
        (Var().val2 == 2)
    )
    assert predicate({'val1': 1, 'val2': 2})
    assert not predicate({'val1': 1})
    assert not predicate({'val2': 2})
    assert not predicate({'val1': '', 'val2': ''})
    assert hash(predicate)


def test_not():
    predicate = ~(Var().val1 == 1)
    assert predicate({'val1': 5, 'val2': 2})
    assert not predicate({'val1': 1, 'val2': 2})
    assert hash(predicate)

    predicate = (
        (~ (Var().val1 == 1)) &
        (Var().val2 == 2)
    )
    assert predicate({'val1': '', 'val2': 2})
    assert predicate({'val2': 2})
    assert not predicate({'val1': 1, 'val2': 2})
    assert not predicate({'val1': 1})
    assert not predicate({'val1': '', 'val2': ''})
    assert hash(predicate)


def test_has_key():
    predicate = Var().val3.exists()

    assert predicate({'val3': 1})
    assert not predicate({'val1': 1, 'val2': 2})
    assert hash(predicate)


def test_regex():
    predicate = Var().val.matches(r'\d{2}\.')

    assert predicate({'val': '42.'})
    assert not predicate({'val': '44'})
    assert not predicate({'val': 'ab.'})
    assert not predicate({'': None})
    assert hash(predicate)

    predicate = Var().val.search(r'\d+')

    assert predicate({'val': 'ab3'})
    assert not predicate({'val': 'abc'})
    assert not predicate({'val': ''})
    assert not predicate({'': None})
    assert hash(predicate)


def test_custom():
    def test(value):
        return value == 42

    predicate = Var().val.test(test)

    assert predicate({'val': 42})
    assert not predicate({'val': 40})
    assert not predicate({'val': '44'})
    assert not predicate({'': None})
    assert hash(predicate)


def test_custom_with_params():
    def test(value, minimum, maximum):
        return minimum <= value <= maximum

    predicate = Var().val.test(test, 1, 10)

    assert predicate({'val': 5})
    assert not predicate({'val': 0})
    assert not predicate({'val': 11})
    assert not predicate({'': None})
    assert hash(predicate)


def test_any():
    predicate = Var().followers.any(Var().name == 'don')

    assert predicate({'followers': [{'name': 'don'}, {'name': 'john'}]})
    assert not predicate({'followers': 1})
    assert not predicate({})
    assert hash(predicate)

    predicate = Var().followers.any(Var().num.matches('\\d+'))
    assert predicate({'followers': [{'num': '12'}, {'num': 'abc'}]})
    assert not predicate({'followers': [{'num': 'abc'}]})
    assert hash(predicate)

    predicate = Var().followers.any(['don', 'jon'])
    assert predicate({'followers': ['don', 'greg', 'bill']})
    assert not predicate({'followers': ['greg', 'bill']})
    assert not predicate({})
    assert hash(predicate)

    predicate = Var().followers.any([{'name': 'don'}, {'name': 'john'}])
    assert predicate({'followers': [{'name': 'don'}, {'name': 'greg'}]})
    assert not predicate({'followers': [{'name': 'greg'}]})
    assert hash(predicate)


def test_all():
    predicate = Var().followers.all(Var().name == 'don')
    assert predicate({'followers': [{'name': 'don'}]})
    assert not predicate({'followers': [{'name': 'don'}, {'name': 'john'}]})
    assert hash(predicate)

    predicate = Var().followers.all(Var().num.matches('\\d+'))
    assert predicate({'followers': [{'num': '123'}, {'num': '456'}]})
    assert not predicate({'followers': [{'num': '123'}, {'num': 'abc'}]})
    assert hash(predicate)

    predicate = Var().followers.all(['don', 'john'])
    assert predicate({'followers': ['don', 'john', 'greg']})
    assert not predicate({'followers': ['don', 'greg']})
    assert not predicate({})
    assert hash(predicate)

    predicate = Var().followers.all([{'name': 'john'}, {'age': 17}])
    assert predicate({'followers': [{'name': 'john'}, {'age': 17}]})
    assert not predicate({'followers': [{'name': 'john'}, {'age': 18}]})
    assert hash(predicate)


def test_has():
    predicate = Var().key1.key2.exists()
    str(predicate)  # This used to cause a bug...

    assert predicate({'key1': {'key2': {'key3': 1}}})
    assert predicate({'key1': {'key2': 1}})
    assert not predicate({'key1': 3})
    assert not predicate({'key1': {'key1': 1}})
    assert not predicate({'key2': {'key1': 1}})
    assert hash(predicate)

    predicate = Var().key1.key2 == 1

    assert predicate({'key1': {'key2': 1}})
    assert not predicate({'key1': {'key2': 2}})
    assert hash(predicate)

    # Nested has: key exists
    predicate = Var().key1.key2.key3.exists()
    assert predicate({'key1': {'key2': {'key3': 1}}})
    # Not a dict
    assert not predicate({'key1': 1})
    assert not predicate({'key1': {'key2': 1}})
    # Wrong key
    assert not predicate({'key1': {'key2': {'key0': 1}}})
    assert not predicate({'key1': {'key0': {'key3': 1}}})
    assert not predicate({'key0': {'key2': {'key3': 1}}})

    assert hash(predicate)

    # Nested has: check for value
    predicate = Var().key1.key2.key3 == 1
    assert predicate({'key1': {'key2': {'key3': 1}}})
    assert not predicate({'key1': {'key2': {'key3': 0}}})
    assert hash(predicate)

    # Test special methods: regex matches
    predicate = Var().key1.value.matches(r'\d+')
    assert predicate({'key1': {'value': '123'}})
    assert not predicate({'key2': {'value': '123'}})
    assert not predicate({'key2': {'value': 'abc'}})
    assert hash(predicate)

    # Test special methods: regex contains
    predicate = Var().key1.value.search(r'\d+')
    assert predicate({'key1': {'value': 'a2c'}})
    assert not predicate({'key2': {'value': 'a2c'}})
    assert not predicate({'key2': {'value': 'abc'}})
    assert hash(predicate)

    # Test special methods: nested has and regex matches
    predicate = Var().key1.x.y.matches(r'\d+')
    assert predicate({'key1': {'x': {'y': '123'}}})
    assert not predicate({'key1': {'x': {'y': 'abc'}}})
    assert hash(predicate)

    # Test special method: nested has and regex contains
    predicate = Var().key1.x.y.search(r'\d+')
    assert predicate({'key1': {'x': {'y': 'a2c'}}})
    assert not predicate({'key1': {'x': {'y': 'abc'}}})
    assert hash(predicate)

    # Test special methods: custom test
    predicate = Var().key1.int.test(lambda x: x == 3)
    assert predicate({'key1': {'int': 3}})
    assert hash(predicate)


def test_hash():
    s = {
        Var().key1 == 2,
        Var().key1.key2.key3.exists(),
        Var().key1.exists() & Var().key2.exists(),
        Var().key1.exists() | Var().key2.exists(),
    }

    assert (Var().key1 == 2) in s
    assert (Var().key1.key2.key3.exists()) in s
    assert (Var()['key1.key2'].key3.exists()) not in s

    # Commutative property of & and |
    assert (Var().key1.exists() & Var().key2.exists()) in s
    assert (Var().key2.exists() & Var().key1.exists()) in s
    assert (Var().key1.exists() | Var().key2.exists()) in s
    assert (Var().key2.exists() | Var().key1.exists()) in s
