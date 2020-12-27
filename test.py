import pytest

from app import app
from db import init_db


@pytest.fixture
def client():
    app.debug_query = True

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_index(client):
    resp = client.get('/', follow_redirects=True)
    assert 'SQLPi Test Server' in resp.get_data(True)


def test_echo(client):
    resp = client.get('/echo?msg=Hello World!')
    assert resp.get_data(True) == 'Hello World!'


def test_compare(client):
    resp = client.get('/compare/>?val=0')
    assert resp.get_data(True) == str(True)


def test_sql(client):
    resp = client.get('/inject/simple?inject=utf-8')
    assert resp.get_data(True) == str(True)
