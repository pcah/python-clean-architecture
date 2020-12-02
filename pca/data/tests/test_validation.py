import pytest

from pca.data.validation import validated_by


@pytest.fixture
def input_data():
    return {"some": "data"}


class MyError(Exception):
    pass


def test_no_validators(input_data):
    @validated_by()
    def f(input_data):
        return input_data

    assert f(input_data) == input_data


def test_single_validator(input_data):
    def validator(input_data):
        if not input_data:
            raise MyError
        return input_data

    @validated_by(validator)
    def f(input_data):
        return input_data

    assert f(input_data) == input_data

    with pytest.raises(MyError):
        f({})


def test_multiple_validators_not_passing_by_data(input_data):
    def validator_1(input_data):
        pass

    def validator_2(input_data):
        if not input_data:
            raise ValueError

    @validated_by(validator_1, validator_2)
    def f(input_data):
        return input_data

    assert f(input_data) == input_data

    with pytest.raises(ValueError):
        f({})


def test_multiple_validators_passing_by_data(input_data):
    def validator_1(input_data):
        return dict(input_data, some_int=int(input_data["some"]))

    def validator_2(input_data):
        if not input_data.get("some_int"):
            raise MyError

    @validated_by(validator_1, validator_2)
    def f(input_data):
        return input_data

    with pytest.raises(ValueError):
        f(input_data)

    with pytest.raises(MyError):
        f({"some": "0"})

    valid_input_data = {"some": "42"}
    assert f(valid_input_data) == {"some": "42", "some_int": 42}
