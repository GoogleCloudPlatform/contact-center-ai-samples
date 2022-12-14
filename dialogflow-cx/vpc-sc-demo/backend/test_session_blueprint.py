# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests session_blueprint.py."""

import os
from urllib.parse import urlparse

import flask
import pytest
from session_blueprint import (
    session as blueprint,
    login_landing_uri,
    DEBUG_DOMAIN,
    user_service_domain,
)
from mock import patch


@pytest.fixture
def app():
    curr_app = flask.Flask(__name__)
    curr_app.register_blueprint(blueprint)
    curr_app.config["TESTING"] = True
    return curr_app


@pytest.mark.parametrize("base_url,landing_uri,prod,query_params",[
    ('http://localhost:5001/', f'http://{DEBUG_DOMAIN}:3000', '', {}),
    ('http://localhost:8081/', f'http://{DEBUG_DOMAIN}:8080', '', {}),
    ('https://MOCK_PRODUCTION_DOMAIN/', 'https://MOCK_PRODUCTION_DOMAIN', 'true', {}),
    (
        'https://MOCK_PRODUCTION_DOMAIN/', 
        'https://MOCK_PRODUCTION_DOMAIN/?MOCK_KEY=MOCK_VAL', 
        'true', 
        {'MOCK_KEY':'MOCK_VAL'}),
])
def test_login_landing_uri_local(app, base_url, landing_uri, prod, query_params):
    with patch.dict(os.environ,{'PROD':prod}):
        with app.test_request_context(base_url=base_url):
            assert login_landing_uri(flask.request, query_params) == landing_uri


@pytest.mark.parametrize("base_url,prod,domain", [
    ('http://localhost:5001/', '', 'user-service.localhost'),
    ('http://localhost:8081/', '', 'user-service.localhost'),
    ('https://MOCK_PRODUCTION_DOMAIN/', 'true', 'mock_production_domain')
])
def test_user_service_domain(app, base_url, prod, domain):
    with patch.dict(os.environ,{'PROD':prod}):
        with app.test_request_context(base_url=base_url):
            assert user_service_domain(flask.request) == domain


def test_session_route(app):
    mock_domain = 'MOCK_DOMAIN.'
    endpoint = '/session'
    with patch.dict(os.environ,{'PROD':'true'}):
        with app.test_client() as curr_client:
            return_value = curr_client.get(endpoint, base_url=f'https://{mock_domain}')

    parsed_url = urlparse(return_value.request.url)
    cookie_list = sorted(return_value.headers.getlist('Set-Cookie'))
    assert cookie_list[0].startswith('session_id=')
    assert cookie_list[1].startswith('user_logged_in=true')
    assert return_value.headers["Content-Type"] == 'text/html; charset=utf-8'
    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == mock_domain
    assert parsed_url.path == endpoint
    assert return_value.status_code == 302


def test_logout_route(app):
    mock_domain = 'MOCK_DOMAIN.'
    endpoint = '/logout'
    with patch.dict(os.environ,{'PROD':'true'}):
        with app.test_client() as curr_client:
            curr_client.set_cookie(mock_domain, 'session_id', 'MOCK_SESSION_ID')
            curr_client.set_cookie(mock_domain, 'user_logged_in', 'MOCK_SESSION_ID')
            return_value = curr_client.get(endpoint, base_url=f'https://{mock_domain}')
    parsed_url = urlparse(return_value.request.url)
    cookie_list = sorted(return_value.headers.getlist('Set-Cookie'))
    assert cookie_list[0].startswith('session_id=;')
    assert r'Expires=Thu, 01 Jan 1970 00:00:00 GMT' in cookie_list[0]
    assert cookie_list[1].startswith('user_logged_in=;')
    assert r'Expires=Thu, 01 Jan 1970 00:00:00 GMT' in cookie_list[1]
    assert return_value.headers["Content-Type"] == 'text/html; charset=utf-8'
    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == mock_domain
    assert parsed_url.path == endpoint
    assert return_value.status_code == 302
