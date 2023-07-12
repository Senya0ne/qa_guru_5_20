import pytest
from jsonschema.validators import validate

from helper import load_json_schema, reqres_session


def test_requested_page_number():
    page = 2
    schema = load_json_schema('get_user_list.json')

    response = reqres_session.get('/api/users', params={'page': page})

    assert response.status_code == 200
    assert response.json()['page'] == page
    validate(response.json(), schema=schema)


def test_users_list_default_length():
    default_users_count = 6

    response = reqres_session.get('/api/users')

    assert len(response.json()['data']) == default_users_count


def test_single_user_not_found():
    response = reqres_session.get('/api/users/23')

    assert response.status_code == 404
    assert response.text == '{}'


def test_create_user():
    name = "jane"
    job = "job"

    response = reqres_session.post(
        url='/api/users',
        json={
            "name": name,
            "job": job}
    )
    assert response.status_code == 201
    assert response.json()['name'] == name


def test_create_user_schema_validation():
    name = "jane"
    job = "job"
    schema = load_json_schema('post_create_user.json')

    response = reqres_session.post(
        url='/api/users',
        json={
            "name": name,
            "job": job}
    )

    validate(instance=response.json(), schema=schema)


def test_delete_user_returns_204():
    response = reqres_session.delete(url='/api/users/2')

    assert response.status_code == 204
    assert response.text == ''


@pytest.mark.parametrize('id', (1, 2, 3, 4, 5))
def test_get_single_user(id):
    schema = load_json_schema('get_single_user.json')

    response = reqres_session.get(f'/api/users/{id}')

    assert response.status_code == 200
    validate(response.json(), schema=schema)
    assert response.json()['data']['id'] == id


def test_resources_list_default_length():
    default_resources_count = 6
    schema = load_json_schema('get_resources_list.json')

    response = reqres_session.get('/api/unknown')

    assert response.status_code == 200
    assert len(response.json()['data']) == default_resources_count
    validate(response.json(), schema=schema)


@pytest.mark.parametrize('id', (1, 2, 3, 4, 5))
def test_get_single_resource(id):
    schema = load_json_schema('get_single_resource.json')

    response = reqres_session.get(f'/api/unknown/{id}')

    assert response.status_code == 200
    validate(response.json(), schema=schema)
    assert response.json()['data']['id'] == id


@pytest.mark.parametrize('method', ('put', 'patch'))
def test_update_user(method):
    schema = load_json_schema('update_single_user.json')
    request_body = {"name": "morpheus", "job": "zion resident"}

    response = reqres_session.request(method=method, url=f'/api/unknown/{id}', json=request_body)

    assert response.status_code == 200
    validate(response.json(), schema=schema)
    assert response.json()['name'] == request_body['name']
    assert response.json()['job'] == request_body['job']


def test_successful_register():
    schema = load_json_schema('post_register_user.json')
    request_body = {"email": "eve.holt@reqres.in", "password": "pistol"}

    response = reqres_session.post(url='/api/register', json=request_body)

    assert response.status_code == 200
    validate(response.json(), schema=schema)


def test_unsuccesful_register():
    request_body = {"email": "sydney@fife"}

    response = reqres_session.post(url='/api/register', json=request_body)

    assert response.status_code == 400
    assert response.json()['error'] == 'Missing password'


def test_succesful_login():
    schema = load_json_schema('post_login_user.json')
    request_body = {"email": "eve.holt@reqres.in", "password": "cityslicka"}

    response = reqres_session.post(url='/api/login', json=request_body)

    validate(response.json(), schema=schema)
    assert response.status_code == 200
    assert response.json()['token'] == 'QpwL5tke4Pnpja7X4'


def test_unsuccesful_login():
    request_body = {"email": "peter@klaven"}

    response = reqres_session.post(url='/api/login', json=request_body)

    assert response.status_code == 400
    assert response.json()['error'] == 'Missing password'



def test_users_page_with_delay():
    delay = 3
    schema = load_json_schema('get_user_list.json')

    response = reqres_session.get('/api/users', params={'delay': delay})

    assert response.status_code == 200
    assert response.elapsed.total_seconds() >= 3
    validate(response.json(), schema=schema)
