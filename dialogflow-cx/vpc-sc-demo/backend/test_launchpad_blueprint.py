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

"""Unit tests launchpad_blueprint.py."""

import json

import flask
import get_token
import pytest
import requests
from launchpad_blueprint import launchpad as blueprint
from mock import patch
from session_blueprint import session


@pytest.fixture
def app():
    """Fixture for tests on session blueprint."""
    curr_app = flask.Flask(__name__)
    curr_app.register_blueprint(blueprint)
    curr_app.config["TESTING"] = True
    return curr_app


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "project_id,status_code,expected,token_dict,valid",
    [
        (None, 200, {"status": False}, {}, None),
        (
            "MOCK_PROJECT_ID",
            0,
            {"MOCK_KEY": "MOCK_VAL"},
            {
                "response": flask.Response(
                    status=0, response=json.dumps({"MOCK_KEY": "MOCK_VAL"})
                )
            },
            None,
        ),
        (
            "MOCK_PROJECT_ID",
            200,
            {"status": False},
            {"access_token": "MOCK_ACCESS_TOKEN"},
            False,
        ),
        (
            "MOCK_PROJECT_ID",
            200,
            {"status": True},
            {"access_token": "MOCK_ACCESS_TOKEN"},
            True,
        ),
    ],
)
def test_validate_project_id(  # pylint: disable=too-many-arguments,redefined-outer-name
    app,
    project_id,
    status_code,
    expected,
    token_dict,
    valid,
):
    """Test /validate_project_id endpoint."""
    endpoint = "/validate_project_id"
    requests_return_value = requests.Response()
    if valid:
        requests_return_value.status_code = 200
    else:
        requests_return_value.status_code = -1

    with patch.object(get_token, "get_token", return_value=token_dict):
        with patch.object(requests, "get", return_value=requests_return_value):
            with app.test_client() as curr_client:
                mock_domain = "MOCK_DOMAIN."
                return_value = curr_client.get(
                    endpoint,
                    base_url=f"https://{mock_domain}",
                    query_string={"project_id": project_id},
                )
    assert return_value.status_code == status_code
    for curr_response in return_value.response:
        assert json.loads(curr_response.decode()) == expected


@pytest.mark.hermetic
def test_get_principal_notoken(app):  # pylint: disable=redefined-outer-name
    """Test /get_principal endpoint."""
    endpoint = "/get_principal"
    app.register_blueprint(session)
    with app.test_client() as curr_client:
        mock_domain = "MOCK_DOMAIN."
        return_value = curr_client.get(
            endpoint,
            base_url=f"https://{mock_domain}",
        )
    assert return_value.status_code == 302


@pytest.mark.hermetic
def test_get_principal(app):  # pylint: disable=redefined-outer-name
    """Test /get_principal endpoint."""
    endpoint = "/get_principal"
    mock_email = "MOCK_EMAIL"
    app.register_blueprint(session)
    with patch.object(get_token, "get_token", return_value={"email": mock_email}):
        with app.test_client() as curr_client:
            mock_domain = "MOCK_DOMAIN."
            return_value = curr_client.get(
                endpoint,
                base_url=f"https://{mock_domain}",
            )
    assert return_value.status_code == 200
    for curr_response in return_value.response:
        assert curr_response.decode() == json.dumps({"principal": mock_email})
