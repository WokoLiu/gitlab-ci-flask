import random
import string

import pytest

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    return client


def test_get_no_user(client):
    resp = client.get('/users/nouser')
    assert resp.status_code == 404


def test_get_user(client):
    resp = client.get('/users/woko')
    assert resp.status_code == 200
    assert resp.json == {'id': 1, 'username': 'woko'}


def test_get_all_users(client):
    resp = client.get('/users')
    assert resp.status_code == 200
    # 顺序问题
    assert resp.json == [
        {'id': 1, 'username': 'woko'},
        {'id': 2, 'username': 'liu'},
    ] or resp.json == [
               {'id': 2, 'username': 'liu'},
               {'id': 1, 'username': 'woko'},
           ]


@pytest.fixture(params=[''.join(random.sample(string.ascii_letters, 20))
                        for _ in range(10)])
def rand_name(request):
    return request.param


def test_add_user(client, rand_name):
    resp = client.post('/users', data={'username': rand_name})
    assert resp.status_code == 302
    assert resp.headers['Location'] == 'http://localhost/users/' + rand_name

    resp = client.get('/users/' + rand_name)
    assert resp.status_code == 200
    assert resp.json['username'] == rand_name
