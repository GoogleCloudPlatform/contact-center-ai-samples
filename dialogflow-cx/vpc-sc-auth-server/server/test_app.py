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

"""Unit tests for app.py."""

import base64
import json
import os
from urllib.parse import parse_qs, urlparse

import app
import pytest
import requests
import session
from google.oauth2 import id_token
from mock import patch


@pytest.fixture
def client():
    """Client fixture for testing a flask app."""
    app.app.config["TESTING"] = True
    with app.app.test_client() as curr_client:
        yield curr_client


class MockOAuthRequestReturnObj:  # pylint: disable=too-few-public-methods
    """Mock Class for OAuth API response"""

    def __init__(self) -> None:
        """Create a mock request return, OAuth API."""

    def json(self):
        """Implement json interface for mock object."""
        return {
            "id_token": "MOCK_ID_TOKEN",
            "access_token": "MOCK_ACCESS_TOKEN",
            "refresh_token": "MOCK_REFRESH_TOKEN",
        }


def test_callback(client):  # pylint: disable=redefined-outer-name
    """Start with a blank database."""

    mock_code = "MOCK_CODE"
    mock_return_to = "MOCK_RETURN_TO"
    mock_state = {
        "return_to": mock_return_to,
        "session_id": "MOCK_SESSION_ID",
        "public_pem": "MOCK_PUBLIC_PEM",
    }
    mock_state_encode = base64.b64encode(json.dumps(mock_state).encode())
    with patch.object(
        app, "access_secret_version", return_value={"response": "MOCK_SECRET"}
    ):
        with patch.object(requests, "post", return_value=MockOAuthRequestReturnObj()):
            with patch.object(
                id_token,
                "verify_oauth2_token",
                return_value={
                    "email": "MOCK_EMAIL",
                    "exp": "MOCK_EXPIRATION",
                },
            ):
                with patch.dict(os.environ, {"SESSION_BUCKET": "MOCK_SESSION_BUCKET"}):
                    with patch.object(
                        session, "create", return_value="MOCK_SESSION_ID"
                    ):
                        return_value = client.get(
                            "/callback",
                            query_string={
                                "state": mock_state_encode,
                                "code": mock_code,
                            },
                        )
    parsed_url = urlparse(return_value.request.url)
    assert parse_qs(parsed_url.query)["state"][0].encode() == mock_state_encode
    assert parse_qs(parsed_url.query)["code"][0] == mock_code
    assert return_value.headers["Content-Type"] == "text/html; charset=utf-8"
    assert return_value.headers["Content-Length"] == "215"
    assert return_value.headers["Location"] == mock_return_to
    assert return_value.status_code == 302
