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
import io
import json
import os
import zipfile
from unittest import mock
from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import google.api_core.exceptions
import pytest
import requests
from google.oauth2 import id_token
from mock import patch


@pytest.fixture
def client():
    """Client fixture for testing a flask app."""

    with patch.object(
        google.auth, "default", return_value=("MOCK_CREDENTIALS", "MOCK_PROJECT")
    ):
        import app  # pylint: disable=import-outside-toplevel

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


@pytest.mark.parametrize(
    "session_id,return_to,status_code",
    [(None, None, 403), ("MOCK_SESSION_ID", "http://localhost/MOCK_RETURN_TO", 302)],
)
def test_callback(
    client, session_id, return_to, status_code
):  # pylint: disable=redefined-outer-name
    """Start with a blank database."""

    mock_code = "MOCK_CODE"
    mock_state = {
        "return_to": return_to,
        "session_id": session_id,
        "public_pem": "MOCK_PUBLIC_PEM",
    }
    mock_state_encode = base64.b64encode(json.dumps(mock_state).encode())
    with patch.object(
        google.auth, "default", return_value=("MOCK_CREDENTIALS", "MOCK_PROJECT")
    ):
        import app  # pylint: disable=import-outside-toplevel

        with patch.object(
            app, "access_secret_version", return_value={"response": "MOCK_SECRET"}
        ):
            with patch.object(
                requests, "post", return_value=MockOAuthRequestReturnObj()
            ):
                with patch.object(
                    id_token,
                    "verify_oauth2_token",
                    return_value={
                        "email": "MOCK_EMAIL",
                        "exp": "MOCK_EXPIRATION",
                    },
                ):
                    import session  # pylint: disable=import-outside-toplevel

                    with patch.dict(
                        os.environ, {"SESSION_BUCKET": "MOCK_SESSION_BUCKET"}
                    ):
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
    assert return_value.headers.get("Location", None) == return_to
    assert return_value.status_code == status_code


def test_login(client):  # pylint: disable=redefined-outer-name
    """Test /login endpoint."""
    mock_client_id = "MOCK_CLIENT_ID"
    mock_state = "MOCK_STATE"
    mock_debug_port = "MOCK_DEBUG_PORT"
    with mock.patch.dict(
        os.environ,
        {
            "DEBUG_PORT": mock_debug_port,
            "CLIENT_ID": mock_client_id,
        },
    ):
        return_value = client.get(
            "/login",
            query_string={"state": mock_state},
        )
    parsed_url = urlparse(return_value.request.url)
    assert parse_qs(parsed_url.query)["state"][0] == mock_state
    assert return_value.headers["Content-Type"] == "text/html; charset=utf-8"
    assert return_value.status_code == 302
    location_parsed_url = urlparse(return_value.headers["Location"])
    assert location_parsed_url.scheme == "https"
    assert location_parsed_url.netloc == "accounts.google.com"
    assert location_parsed_url.path == "/o/oauth2/v2/auth"
    assert (
        parse_qs(location_parsed_url.query)["redirect_uri"][0]
        == f"http://localhost:{mock_debug_port}/callback"
    )
    assert parse_qs(location_parsed_url.query)["client_id"][0] == mock_client_id
    assert (
        parse_qs(location_parsed_url.query)["scope"][0]
        == "openid email https://www.googleapis.com/auth/cloud-platform"
    )
    assert parse_qs(location_parsed_url.query)["include_granted_scopes"][0] == "true"
    assert parse_qs(location_parsed_url.query)["prompt"][0] == "consent"
    assert parse_qs(location_parsed_url.query)["access_type"][0] == "offline"
    assert parse_qs(location_parsed_url.query)["response_type"][0] == "code"
    assert parse_qs(location_parsed_url.query)["state"][0] == mock_state


@pytest.mark.parametrize(
    "prod,expected",
    [
        ("true", "https://auth.dialogflow-demo.app/callback"),
        ("false", "http://localhost:{mock_debug_port}/callback"),
    ],
)
def test_get_redirect_url(prod, expected):
    """Test test_get_redirect_url under prod and dev behavior."""
    mock_debug_port = "MOCK_DEBUG_PORT"
    with patch.object(
        google.auth, "default", return_value=("MOCK_CREDENTIALS", "MOCK_PROJECT")
    ):
        import app  # pylint: disable=import-outside-toplevel

        with mock.patch.dict(os.environ, {"PROD": prod, "DEBUG_PORT": mock_debug_port}):
            assert app.get_redirect_url() == expected.format(
                mock_debug_port=mock_debug_port
            )


def get_aut_endpoint_response(curr_client, mock_blob, mock_session_id):
    """Return response from a mocked /auth endpoint."""
    with patch.dict(os.environ, {"SESSION_BUCKET": "MOCK_SESSION_BUCKET"}):
        import google.cloud.storage as storage  # pylint: disable=import-outside-toplevel,consider-using-from-import

        with patch.object(storage.blob, "Blob", return_value=mock_blob):
            return curr_client.get(
                "/auth",
                query_string={"session_id": mock_session_id},
            )


def test_auth(client):  # pylint: disable=redefined-outer-name
    """Test /auth route."""

    mock_key = b"MOCK_KEY"
    mock_session_data = b"MOCK_SESSION_DATA"
    mock_session_id = "MOCK_SESSION_ID"
    mock_blob = Mock()
    mock_blob.download_as_bytes = Mock()
    mock_blob.download_as_bytes.side_effect = [mock_key, mock_session_data]

    return_value = get_aut_endpoint_response(client, mock_blob, mock_session_id)
    parsed_url = urlparse(return_value.request.url)
    assert parsed_url.scheme == "http"
    assert parsed_url.netloc == "localhost"
    assert parsed_url.path == "/auth"
    assert parse_qs(parsed_url.query)["session_id"][0] == mock_session_id
    assert return_value.headers["Content-Type"] == "application/zip"
    assert (
        return_value.headers["Content-Disposition"]
        == "attachment; filename=encrypted_session.zip"
    )
    assert return_value.headers["Cache-Control"] == "no-cache"
    assert return_value.status_code == 200
    for curr_response in return_value.response:
        with zipfile.ZipFile(io.BytesIO(curr_response)) as zip_file:
            assert mock_key == zip_file.read("key")
            assert mock_session_data == zip_file.read("session_data")


def test_auth_bad_session(client):  # pylint: disable=redefined-outer-name
    """Test /auth route, with a session_id that doesnt exist."""
    mock_session_id = "MOCK_SESSION_ID"
    mock_blob = Mock()
    import session  # pylint: disable=import-outside-toplevel

    def download_as_bytes_mock():
        raise google.api_core.exceptions.NotFound(session.NOT_FOUND_ERROR_MESSAGE)

    mock_blob.download_as_bytes = download_as_bytes_mock

    return_value = get_aut_endpoint_response(client, mock_blob, mock_session_id)
    parsed_url = urlparse(return_value.request.url)
    assert parsed_url.scheme == "http"
    assert parsed_url.netloc == "localhost"
    assert parsed_url.path == "/auth"
    assert parse_qs(parsed_url.query)["session_id"][0] == mock_session_id
    assert return_value.headers["Content-Type"] == "text/html; charset=utf-8"
    assert return_value.status_code == 401
    for curr_response in return_value.response:
        assert curr_response == f"{session.NOT_FOUND_ERROR_MESSAGE}".encode()
