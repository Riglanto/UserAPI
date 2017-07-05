from falcon import testing
import pytest
import server

params = {
    'username': 'user1',
    'password': 'password1234',
}


@pytest.fixture
def client():
    server.get_db().purge()
    return testing.TestClient(server.create())


def test_register(client):
    result = client.simulate_post('/register', params=params)
    assert result.status_code == 200


def test_register_fail(client):
    client.simulate_post('/register', params=params)
    result = client.simulate_post('/register', params=params)

    assert result.status_code == 400
    assert result.json['title'] == 'User already exists'


def test_login(client):
    client.simulate_post('/register', params=params)
    client.simulate_post('/login', params=params)
    client.simulate_post('/login', params=params)
    result = client.simulate_post('/login', params=params)

    assert result.status_code == 200
    assert len(result.json) == 3


def test_login_no_user(client):
    result = client.simulate_post('/login', params=params)

    assert result.status_code == 400
    assert result.json['title'] == 'User does not exist'


def test_login_no_user(client):
    incorrect_params = {
        'username': 'user1',
        'password': 'bad_password'
    }

    client.simulate_post('/register', params=params)
    result = client.simulate_post('/login', params=incorrect_params)

    assert result.status_code == 400
    assert result.json['title'] == 'Incorrect password'
