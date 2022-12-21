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

"""Tests for update_blueprint.py."""

import flask
import pytest
from mock import patch

from conftest import assert_response_ep as assert_response, MOCK_DOMAIN
import get_token
from update_blueprint import update as blueprint


@pytest.fixture
def app():
    """Fixture for tests on session blueprint."""
    curr_app = flask.Flask(__name__)
    curr_app.register_blueprint(blueprint)
    curr_app.config["TESTING"] = True
    return curr_app


def get_result(
    curr_app,
    endpoint,
):
    """Helper function to get result from a test client."""
    with curr_app.test_client() as curr_client:
        return curr_client.post(
            endpoint,
            base_url=f"https://{MOCK_DOMAIN}",
        )


@pytest.mark.parametrize(
    "endpoint",
    [
        "/update_webhook_access",
        "/update_webhook_ingress",
        "/update_security_perimeter_cloudfunctions",
        "/update_security_perimeter_dialogflow",
        "/update_service_directory_webhook_fulfillment",
    ],
)
@patch.object(
    get_token, "get_token", return_value={"response": "MOCK_RESPONSE"}
)
def test_endpoints_bad_token(get_token_mock, app, endpoint):  # pylint: disable=redefined-outer-name
    """Test endpoints, bad token"""
    return_value = get_result(app, endpoint)
    assert_response(return_value, 200, endpoint, "MOCK_RESPONSE")
    get_token_mock.assert_called_once()
    