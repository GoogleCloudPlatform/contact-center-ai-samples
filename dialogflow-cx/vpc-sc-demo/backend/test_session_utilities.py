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

"""Utilities module for session blueprint."""

import os

import flask
import pytest
import session_utilities as su
from mock import patch
from session_blueprint import DEBUG_DOMAIN
from session_blueprint import session as blueprint


@patch.dict(os.environ, {"PROD": "true"})
def test_is_prod_true():
    """Test is_prod indicator, True"""
    assert su.is_prod()


@patch.dict(os.environ, {"PROD": ""})
def test_is_prod_false():
    """Test is_prod indicator, False"""
    assert not su.is_prod()


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,base_url,landing_uri,prod,query_params",
    [
        (blueprint, "http://localhost:5001/", f"http://{DEBUG_DOMAIN}:3000", "", {}),
        (blueprint, "http://localhost:8081/", f"http://{DEBUG_DOMAIN}:8080", "", {}),
        (
            blueprint,
            "https://MOCK_PRODUCTION_DOMAIN/",
            "https://MOCK_PRODUCTION_DOMAIN",
            "true",
            None,
        ),
        (
            blueprint,
            "https://MOCK_PRODUCTION_DOMAIN/",
            "https://MOCK_PRODUCTION_DOMAIN/?MOCK_KEY=MOCK_VAL",
            "true",
            {"MOCK_KEY": "MOCK_VAL"},
        ),
    ],
    indirect=["app"],
)
def test_login_landing_uri_local(
    app,
    base_url,
    landing_uri,
    prod,
    query_params,
):
    """Test login_landing_uri_local."""
    with patch.dict(os.environ, {"PROD": prod}):
        with app.test_request_context(base_url=base_url):
            assert su.login_landing_uri(flask.request, query_params) == landing_uri


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "app,base_url,prod,domain",
    [
        (blueprint, "http://localhost:5001/", "", "user-service.localhost"),
        (blueprint, "http://localhost:8081/", "", "user-service.localhost"),
        (
            blueprint,
            "https://MOCK_PRODUCTION_DOMAIN/",
            "true",
            "mock_production_domain",
        ),
    ],
    indirect=["app"],
)
def test_user_service_domain(
    app, base_url, prod, domain
):  # pylint: disable=redefined-outer-name
    """Test user_service_domain method."""
    with patch.dict(os.environ, {"PROD": prod}):
        with app.test_request_context(base_url=base_url):
            assert su.user_service_domain(flask.request) == domain
