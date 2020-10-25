
import pytest

from flask import session

def test_register(client):
    # Check that we retrieve the register page.
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid username and password.
    response = client.post(
        '/authentication/register',
        data={'username': 'gmichael', 'password': 'CarelessWhisper1984'}
    )
    assert response.headers['Location'] == 'http://localhost/authentication/login'


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Your username is required'),
        ('cj', '', b'Your username is too short'),
        ('test', '', b'Your password is required'),
        ('test', 'test', b'Your password must be at least 8 characters, and contain an upper case letter,\
            a lower case letter and a digit'),
        ('fmercury', 'Test#6^0', b'Your username is already taken - please supply another'),
))
def test_register_with_invalid_input(client, username, password, message):
    # Check that attempting to register with invalid combinations of username and password generate appropriate error
    # messages.
    response = client.post(
        '/authentication/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    # Check that we can retrieve the login page.
    status_code = client.get('/authentication/login').status_code
    assert status_code == 200

    # Check that a successful login generates a redirect to the homepage.
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    # Check that a session has been created for the logged-in user.
    with client:
        client.get('/')
        assert session['username'] == 'thorke'


def test_logout(client, auth):
    # Login a user.
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        auth.logout()
        assert 'user_id' not in session


def test_index(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200

def test_comment(client, auth):
    # Login a user.
    auth.login()

    # Check that we can retrieve the comment page.

    response = client.post(
        '/comment/2',
        data={'review': 'Who needs movies?', 'rating': 2}
    )
    print(response.headers)
    assert response.headers['Location'] == 'http://localhost/movie/2'

def test_first_page_movies(client):
    # Check that we can retrieve the first movies page.
    response = client.get('/all_movies/0')
    assert response.status_code == 200

def test_last_page_movies(client):
    # Check that we can retrieve the last movies page.
    response = client.get('/all_movies/-1')
    assert response.status_code == 200

def test_articles_with_comment(client):
    # Check that we can retrieve the articles page.
    response = client.get('/movie/1')
    assert response.status_code == 200

    # Check that all comments for specified article are included on the page.
    assert b'Oh no, csflix has hit New Zealand' in response.data
    assert b'Yeah Freddie, bad news' in response.data
