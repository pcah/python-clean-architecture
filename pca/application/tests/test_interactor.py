import typing as t

import mock
import pytest

from pca.application.interactor import (
    interactor_factory,
    ResponseModel,
    RequestModel,
)
from pca.domain.entity import Entity
from pca.domain.repository import Repository
from pca.exceptions import LogicError
from pca.utils.dependency_injection import Inject


class Racer(Entity):
    first_name: str
    last_name: str


class Team(Entity):
    name: str
    members: t.List[Racer]  # TODO: initial empty list


@pytest.fixture
def team():
    return Team(name='name', members=[])


@pytest.fixture
def racer():
    return Racer(first_name='first_name', last_name='last_name')


@pytest.fixture(autouse=True)
def teams(container, team):
    repo = mock.Mock(spec=Repository)
    repo.find.return_value = team
    container.register_by_interface(Repository, lambda *args: repo, qualifier=Team)
    return repo


@pytest.fixture(autouse=True)
def racers(container, racer):
    repo = mock.Mock(spec=Repository)
    repo.find.return_value = racer
    container.register_by_interface(Repository, lambda *args: repo, qualifier=Racer)
    return repo


@pytest.fixture
def input_data():
    return {'team_id': 1, 'racer_id': 7}


def add_team_member(
        input_data: RequestModel,
        teams: Repository = Inject(qualifier=Team),
        racers: Repository = Inject(qualifier=Racer),
):
    team: Team = teams.find(input_data['team_id'])
    racer: Racer = racers.find(input_data['racer_id'])
    team.members.append(racer)
    teams.update(team)
    return ResponseModel(data=input_data, errors={})


class TestFunctionInteractor:

    @pytest.fixture
    def error_result(self):
        return {'error': 42}

    @pytest.fixture
    def error_handler(self, error_result):
        return mock.Mock(return_value=error_result)

    @pytest.fixture
    def interactor_function(self, error_handler):
        return interactor_factory(error_handler=error_handler)

    @pytest.fixture
    def validators(self, input_data):
        validator_1 = mock.Mock()
        validator_1.return_value = input_data
        validator_2 = mock.Mock()
        validator_2.return_value = input_data
        return (validator_1, validator_2)

    def test_wo_validation(self, container, interactor_function, input_data, team, teams, racers):
        interactor = interactor_function()(add_team_member)(container)

        result = interactor(input_data)

        assert result.data == input_data
        assert result.is_success
        racers.find.assert_called_once_with(input_data['racer_id'])
        teams.find.assert_called_once_with(input_data['team_id'])
        teams.update.assert_called_once_with(team)

    def test_validation_passing_ok(
            self, container, interactor_function, input_data, teams, team, racers, validators):
        interactor = interactor_function(*validators)(add_team_member)(container)

        result = interactor(input_data)

        assert result.data == input_data
        assert result.is_success
        teams.find.assert_called_once_with(input_data['team_id'])
        racers.find.assert_called_once_with(input_data['racer_id'])
        teams.update.assert_called_once_with(team)
        validators[0].assert_called_once_with(input_data, racers=racers, teams=teams)
        validators[1].assert_called_once_with(input_data, racers=racers, teams=teams)

    def test_late_validation_error_caught(
            self, container, interactor_function, error_result, error_handler, input_data,
            validators, teams, racers):
        error_instance = LogicError('foo')
        validators[1].side_effect = error_instance
        interactor = interactor_function(*validators)(add_team_member)(container)

        result = interactor(input_data)

        assert result == error_result
        validators[0].assert_called_once_with(input_data, racers=racers, teams=teams)
        validators[1].assert_called_once_with(input_data, racers=racers, teams=teams)
        error_handler.assert_called_once_with(
            error=error_instance,
            function_name='pca.application.tests.test_interactor.add_team_member',
            args=(input_data,),
            kwargs={'teams': teams, 'racers': racers}
        )

    def test_early_validation_error_caught(
            self, container, interactor_function, error_result, error_handler, input_data,
            validators, teams, racers):
        error_instance = LogicError('foo')
        validators[0].side_effect = error_instance
        interactor = interactor_function(*validators)(add_team_member)(container)

        result = interactor(input_data)

        assert result == error_result
        validators[0].assert_called_once_with(input_data, racers=racers, teams=teams)
        validators[1].assert_not_called()
        error_handler.assert_called_once_with(
            error=error_instance,
            function_name='pca.application.tests.test_interactor.add_team_member',
            args=(input_data,),
            kwargs={'teams': teams, 'racers': racers}
        )

    def test_validation_error_not_caught(
            self, container, interactor_function, error_handler, input_data, validators,
            teams, racers):
        error_instance = ValueError()
        validators[0].side_effect = error_instance
        interactor = interactor_function(*validators)(add_team_member)(container)

        with pytest.raises(ValueError):
            interactor(input_data)

        validators[0].assert_called_once_with(input_data, racers=racers, teams=teams)
        validators[1].assert_not_called()
        error_handler.assert_not_called()

    def test_interactor_error_caught(
            self, container, interactor_function, error_handler, input_data, validators):
        error_instance = LogicError('foo')
        interactor_mock = mock.Mock(side_effect=error_instance)
        interactor = interactor_function(*validators)(interactor_mock)(container)

        interactor(input_data)

        validators[0].assert_called_once_with(input_data)
        validators[1].assert_called_once_with(input_data)
        interactor_mock.assert_called_once_with(input_data)
        error_handler.assert_called_once_with(
            error=error_instance,
            function_name='mock.mock.validated_by.<locals>.decorator.<locals>.decorated',
            args=(input_data,),
            kwargs={}
        )

    def test_interactor_error_not_caught(
            self, container, interactor_function, error_handler, input_data, validators):
        error_instance = ValueError()
        interactor_mock = mock.Mock(side_effect=error_instance)
        interactor = interactor_function(*validators)(interactor_mock)(container)

        with pytest.raises(ValueError):
            interactor(input_data)

        validators[0].assert_called_once_with(input_data)
        validators[1].assert_called_once_with(input_data)
        interactor_mock.assert_called_once_with(input_data)
        error_handler.assert_not_called()

    def test_multiple_error_class(
            self, container, error_handler, input_data, validators):
        error_instance = ValueError()
        interactor_mock = mock.Mock(side_effect=error_instance)
        interactor_function = interactor_factory(
            error_class=(LogicError, ValueError),
            error_handler=error_handler
        )
        interactor = interactor_function(*validators)(interactor_mock)(container)

        interactor(input_data)

        validators[0].assert_called_once_with(input_data)
        validators[1].assert_called_once_with(input_data)
        interactor_mock.assert_called_once_with(input_data)
        error_handler.assert_called_once_with(
            error=error_instance,
            function_name='mock.mock.validated_by.<locals>.decorator.<locals>.decorated',
            args=(input_data,),
            kwargs={}
        )
