import typing as t

import mock
import pytest

from pca.application.interactor import (
    interactor_function,
    ResponseModel,
    RequestModel,
)
from pca.domain.entity import Entity
from pca.domain.repository import Repository
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

    def test_wo_validation(self, container, input_data, team, teams, racers):
        interactor = interactor_function()(add_team_member)(container)

        response = interactor(input_data)

        assert response.data == input_data
        assert response.is_success
        racers.find.assert_called_once_with(input_data['racer_id'])
        teams.find.assert_called_once_with(input_data['team_id'])
        teams.update.assert_called_once_with(team)

    @pytest.fixture
    def validators(self, input_data):
        validator_1 = mock.Mock()
        validator_1.return_value = input_data
        validator_2 = mock.Mock()
        validator_2.return_value = input_data
        return (validator_1, validator_2)

    def test_validation_passing_ok(self, container, input_data, teams, team, racers, validators):
        interactor = interactor_function(*validators)(add_team_member)(container)

        response = interactor(input_data)

        assert response.data == input_data
        assert response.is_success
        teams.find.assert_called_once_with(input_data['team_id'])
        racers.find.assert_called_once_with(input_data['racer_id'])
        teams.update.assert_called_once_with(team)

    def test_interactor_exceptions(self, container, input_data, teams, team, racers, validators):
        # TODO #4.
        pass

    def test_validation_exceptions(self, container, input_data, teams, team, racers, validators):
        # TODO #4.
        pass
