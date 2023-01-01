"""
Sets up an app for tests
"""

import json
import os
import sys

try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request, build_opener, HTTPHandler
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError, build_opener, HTTPHandler


EMAIL = os.environ['CLARIFAI_USER_EMAIL']
PASSWORD = os.environ['CLARIFAI_USER_PASSWORD']


def _assert_response_success(response):
    assert 'status' in response, f'Invalid response {response}'
    assert 'code' in response['status'], f'Invalid response {response}'
    assert response['status']['code'] == 10000, f'Invalid response {response}'


def _request(method, url, payload={}, headers={}):
    base_url = os.environ.get('CLARIFAI_GRPC_BASE', 'api.clarifai.com')

    opener = build_opener(HTTPHandler)
    full_url = f'https://{base_url}/v2{url}'
    request = Request(full_url, data=json.dumps(payload).encode())
    for k in headers.keys():
        request.add_header(k, headers[k])
    request.get_method = lambda: method
    try:
        response = opener.open(request).read().decode()
    except HTTPError as e:
        error_body = e.read().decode()
        try:
            error_body = json.dumps(json.loads(error_body), indent=4)
        except:
            pass
        raise Exception("ERROR after a HTTP request to: %s %s" % (method, full_url)
                        + ". Response: %d %s:\n%s" % (e.code, e.reason, error_body))
    return json.loads(response)


def create_app(env_name):
    session_token, user_id = _login()

    url = '/users/%s/apps' % user_id
    payload = {'apps': [{'name': 'auto-created-in-%s-ci-test-run' % env_name}]}

    data = _request(method='POST', url=url, payload=payload, headers=_auth_headers(session_token))
    _assert_response_success(data)

    assert 'apps' in data, f'Invalid response {data}'
    assert len(data['apps']) == 1, f'Invalid response {data}'
    assert 'id' in data['apps'][0], f'Invalid response {data}'
    app_id = data['apps'][0]['id']
    assert app_id, f'Invalid response {data}'

    # This print needs to be present so we can read the value in CI.
    print(app_id)


def create_key(app_id):
    session_token, user_id = _login()

    url = '/users/%s/keys' % user_id
    payload = {
        'keys': [{
            'description': 'Auto-created in a CI test run',
            'scopes': ['All'],
            'apps': [{'id': app_id, 'user_id': user_id}]
        }]
    }
    data = _request(method='POST', url=url, payload=payload, headers=_auth_headers(session_token))
    _assert_response_success(data)

    assert 'keys' in data, f'Invalid response {data}'
    assert len(data['keys']) == 1, f'Invalid response {data}'
    assert 'id' in data['keys'][0], f'Invalid response {data}'
    key_id = data['keys'][0]['id']
    assert key_id, f'Invalid response {data}'

    # This print needs to be present so we can read the value in CI.
    print(key_id)


def delete(app_id):
    session_token, user_id = _login()

    # All the related keys will be deleted automatically when the app is deleted
    _delete_app(session_token, user_id, app_id)


def _delete_app(session_token, user_id, app_id):
    url = '/users/%s/apps/%s' % (user_id, app_id)
    response = _request(method='DELETE', url=url, headers=_auth_headers(session_token))
    _assert_response_success(response)


def _auth_headers(session_token):
    headers = {'Content-Type': 'application/json', 'X-Clarifai-Session-Token': session_token}
    return headers


def _auth_headers_for_api_key_key(api_key):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Key ' + api_key}
    return headers


def _login():
    url = '/login'
    payload = {'email': EMAIL, 'password': PASSWORD}
    data = _request(method='POST', url=url, payload=payload)
    _assert_response_success(data)

    assert 'v2_user_id' in data, f'Invalid response {data}'
    user_id = data['v2_user_id']
    assert user_id, f'Invalid response {data}'

    assert 'session_token' in data, f'Invalid response {data}'
    session_token = data['session_token']
    assert session_token, f'Invalid response {data}'

    return session_token, user_id


def run(arguments):
    command = arguments[0] if arguments else '--help'
    if command == '--create-app':
        if len(arguments) != 2:
            raise Exception('--create-app takes one argument')

        env_name = arguments[1]
        create_app(env_name)
    elif command == '--create-key':
        if len(arguments) != 2:
            raise Exception('--create-key takes one argument')

        app_id = arguments[1]
        create_key(app_id)
    elif command == '--delete-app':
        if len(arguments) != 2:
            raise Exception('--delete-app takes one argument')
        app_id = arguments[1]
        delete(app_id)
    elif command == '--help':
        print('''DESCRIPTION: Creates and delete applications and API keys
ARGUMENTS:
--create-app [env_name]      ... Creates a new application.
--create-key [app_id]        ... Creates a new API key.
--delete-app [app_id]        ... Deletes an application (API keys that use it are deleted as well).
--help                       ... This text.''')
    else:
        print('Unknown argument. Please see --help')
        exit(1)


if __name__ == '__main__':
    run(arguments=sys.argv[1:])