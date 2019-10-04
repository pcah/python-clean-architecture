import typing as t

import mock
import pytest

from pca.application.interactor import (
    Interactor,
    ResponseModel,
    RequestModel,
    interactor_factory,
)
from pca.domain.entity import Entity, field
from pca.domain.repository import Repository
from pca.exceptions import LogicError
from pca.utils.dependency_injection import (
    Inject,
    create_component,
    get_attribute_dependencies,
)


class Racer(Entity):
    first_name: str
    last_name: str


class Team(Entity):
    name: str
    members: t.List[Racer] = field(default_factory=list)


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
def request_data():
    return {'team_id': 1, 'racer_id': 7}


@pytest.fixture
def error_result():
    return {'error': 42}


@pytest.fixture
def validators(request_data):
    validator_1 = mock.Mock()
    validator_1.return_value = request_data
    validator_2 = mock.Mock()
    validator_2.return_value = request_data
    return (validator_1, validator_2)


def add_team_member(
        request_data: RequestModel,
        teams: Repository = Inject(qualifier=Team),
        racers: Repository = Inject(qualifier=Racer),
):
    team: Team = teams.find(request_data['team_id'])
    racer: Racer = racers.find(request_data['racer_id'])
    team.members.append(racer)
    teams.update(team)
    return ResponseModel(data=request_data, errors={})


class TestFunctionInteractor:

    @pytest.fixture
    def error_handler(self, error_result):
        return mock.Mock(return_value=error_result)

    @pytest.fixture
    def interactor_function(self, error_handler):
        return interactor_factory(error_handler=error_handler)

    def test_wo_validation(
            self, container, interactor_function, request_data, team, teams, racers
    ):
        interactor = interactor_function()(add_team_member)(container)

        response = interactor(request_data)

        assert response.data == request_data
        assert response.is_success
        racers.find.assert_called_once_with(request_data['racer_id'])
        teams.find.assert_called_once_with(request_data['team_id'])
        teams.update.assert_called_once_with(team)

    def test_validation_passing_ok(
            self, container, interactor_function, request_data, teams, team, racers, validators):
        interactor = interactor_function(*validators)(add_team_member)(container)

        result = interactor(request_data)

        assert result.data == request_data
        assert result.is_success
        teams.find.assert_called_once_with(request_data['team_id'])
        racers.find.assert_called_once_with(request_data['racer_id'])
        teams.update.assert_called_once_with(team)
        validators[0].assert_called_once_with(request_data, racers=racers, teams=teams)
        validators[1].assert_called_once_with(request_data, racers=racers, teams=teams)

    def test_late_validation_error_caught(
            self, container, interactor_function, error_result, error_handler, request_data,
            validators, teams, racers):
        error_instance = LogicError('foo')
        validators[1].side_effect = error_instance
        interactor = interactor_function(*validators)(add_team_member)(container)

        result = interactor(request_data)

        assert result == error_result
        validators[0].assert_called_once_with(request_data, racers=racers, teams=teams)
        validators[1].assert_called_once_with(request_data, racers=racers, teams=teams)
        error_handler.assert_called_once_with(
            error=error_instance,
            function_name='pca.application.tests.test_interactor.add_team_member',
            args=(request_data,),
            kwargs={'teams': teams, 'racers': racers}
        )

    def test_early_validation_error_caught(
            self, container, interactor_function, error_result, error_handler, request_data,
            validators, teams, racers):
        error_instance = LogicError('foo')
        validators[0].side_effect = error_instance
        interactor = interactor_function(*validators)(add_team_member)(container)

        result = interactor(request_data)

        assert result == error_result
        validators[0].assert_called_once_with(request_data, racers=racers, teams=teams)
        validators[1].assert_not_called()
        error_handler.assert_called_once_with(
            error=error_instance,
            function_name='pca.application.tests.test_interactor.add_team_member',
            args=(request_data,),
            kwargs={'teams': teams, 'racers': racers}
        )

    def test_validation_error_not_caught(
            self, container, interactor_function, error_handler, request_data, validators,
            teams, racers):
        error_instance = ValueError()
        validators[0].side_effect = error_instance
        interactor = interactor_function(*validators)(add_team_member)(container)

        with pytest.raises(ValueError):
            interactor(request_data)

        validators[0].assert_called_once_with(request_data, racers=racers, teams=teams)
        validators[1].assert_not_called()
        error_handler.assert_not_called()

    def test_interactor_error_caught(
            self, container, interactor_function, error_handler, request_data, validators):
        error_instance = LogicError('foo')
        interactor_mock = mock.Mock(side_effect=error_instance)
        interactor = interactor_function(*validators)(interactor_mock)(container)

        interactor(request_data)

        validators[0].assert_called_once_with(request_data)
        validators[1].assert_called_once_with(request_data)
        interactor_mock.assert_called_once_with(request_data)
        error_handler.assert_called_once_with(
            error=error_instance,
            function_name='mock.mock.validated_by.<locals>.decorator.<locals>.decorated',
            args=(request_data,),
            kwargs={}
        )

    def test_interactor_error_not_caught(
            self, container, interactor_function, error_handler, request_data, validators):
        error_instance = ValueError()
        interactor_mock = mock.Mock(side_effect=error_instance)
        interactor = interactor_function(*validators)(interactor_mock)(container)

        with pytest.raises(ValueError):
            interactor(request_data)

        validators[0].assert_called_once_with(request_data)
        validators[1].assert_called_once_with(request_data)
        interactor_mock.assert_called_once_with(request_data)
        error_handler.assert_not_called()

    def test_multiple_error_class(
            self, container, error_handler, request_data, validators):
        error_instance = ValueError()
        interactor_mock = mock.Mock(side_effect=error_instance)
        interactor_function = interactor_factory(
            error_class=(LogicError, ValueError),
            error_handler=error_handler
        )
        interactor = interactor_function(*validators)(interactor_mock)(container)

        interactor(request_data)

        validators[0].assert_called_once_with(request_data)
        validators[1].assert_called_once_with(request_data)
        interactor_mock.assert_called_once_with(request_data)
        error_handler.assert_called_once_with(
            error=error_instance,
            function_name='mock.mock.validated_by.<locals>.decorator.<locals>.decorated',
            args=(request_data,),
            kwargs={}
        )


class AddTeamMember(Interactor):

    teams: Repository = Inject(qualifier=Team)
    racers: Repository = Inject(qualifier=Racer)

    def __init__(self, validators):
        # testing properties; normally, validators would be just a property with functions declared
        self.error_handler = mock.MagicMock(return_value={'error': 42})
        self.validators = validators

    def handle_error(self, error: Exception, request: RequestModel):
        return self.error_handler(error=error, request=request)

    def execute(self, request: RequestModel) -> ResponseModel:
        team: Team = self.teams.find(request['team_id'])
        racer: Racer = self.racers.find(request['racer_id'])
        team.members.append(racer)
        self.teams.update(team)
        return ResponseModel(data=request, errors={})


class TestClassInteractor:

    @pytest.fixture
    def interactor(self, container, validators):
        return create_component(AddTeamMember, container, kwargs={'validators': validators})

    def test_without_validation(self, container, request_data, team):
        interactor = create_component(AddTeamMember, container, kwargs={'validators': ()})
        response = interactor(request_data)

        assert response.data == request_data
        assert not response.errors
        assert response.is_success
        # noinspection PyUnresolvedReferences
        interactor.teams.update.assert_called_once_with(team)

    def test_validation_passing_ok(self, interactor, request_data, team):
        response = interactor(request_data)

        assert response.data == request_data
        assert not response.errors
        assert response.is_success
        interactor.teams.update.assert_called_once_with(team)

    def test_late_validation_error_caught(
            self, interactor, request_data, error_result, validators
    ):
        error_instance = LogicError('foo')
        validators[1].side_effect = error_instance

        response = interactor(request_data)
        dependencies = get_attribute_dependencies(interactor)

        assert response == error_result
        validators[0].assert_called_once_with(request=request_data, dependencies=dependencies)
        validators[1].assert_called_once_with(request=request_data, dependencies=dependencies)
        interactor.error_handler.assert_called_once_with(
            error=error_instance, request=request_data)

    def test_interactor_error_not_caught(self, interactor, request_data, validators, teams):
        error_instance = ValueError()
        teams.find.side_effect = error_instance

        with pytest.raises(ValueError):
            interactor(request_data)
        dependencies = get_attribute_dependencies(interactor)

        validators[0].assert_called_once_with(request=request_data, dependencies=dependencies)
        validators[1].assert_called_once_with(request=request_data, dependencies=dependencies)
        teams.find.assert_called_once_with(request_data['team_id'])
        interactor.error_handler.assert_not_called()

    def test_multiple_error_class(self, interactor, request_data, validators, error_result, teams):
        error_instance = ValueError()
        interactor.error_class = (LogicError, ValueError)
        teams.find.side_effect = error_instance

        response = interactor(request_data)
        dependencies = get_attribute_dependencies(interactor)

        assert response == error_result
        validators[0].assert_called_once_with(request=request_data, dependencies=dependencies)
        validators[1].assert_called_once_with(request=request_data, dependencies=dependencies)
        teams.find.assert_called_once_with(request_data['team_id'])
        interactor.error_handler.assert_called_once_with(
            error=error_instance, request=request_data)
