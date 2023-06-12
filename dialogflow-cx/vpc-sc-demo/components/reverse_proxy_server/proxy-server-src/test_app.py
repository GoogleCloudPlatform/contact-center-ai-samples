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


import os
import signal
from urllib.parse import urlparse

import pytest
import requests
from flask.testing import FlaskClient
from google.oauth2 import id_token
from mock import patch
from werkzeug.exceptions import Forbidden

_DEFAULT_VERIFY_TOKEN_METHOD = "verify_oauth2_token"


class CustomClient(FlaskClient):
    """Custom FlaskClient for testing different headers."""

    def __init__(self, *args, **kwargs):
        self.headers = kwargs.pop("headers", {})
        self.status_code = kwargs.pop("status_code", {})
        super().__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        headers = kwargs.setdefault("headers", {})
        for key, val in self.headers.items():
            headers.setdefault(key, val)
        return super().open(*args, **kwargs)


class MockRequestReturnObj:  # pylint: disable=too-few-public-methods
    """Mock Class for OAuth API response"""

    text = "MOCK_TEXT"

    def __init__(self, status_code, text) -> None:
        """Create a mock request return, OAuth API."""
        self.status_code = status_code
        self.text = text


@pytest.fixture
def client(request):
    """Client fixture for testing a flask app."""

    mock_allowed_user = "MOCK_BOT_USER"

    with patch.dict(
        os.environ,
        {
            "BOT_USER": mock_allowed_user,
            "WEBHOOK_TRIGGER_URI": "http://MOCK_WEBHOOK_TRIGGER_URI",
        },
    ):
        with patch.object(
            id_token,
            request.param.get("verify_token_method", _DEFAULT_VERIFY_TOKEN_METHOD),
            return_value={"email": mock_allowed_user},
        ):
            return_value = MockRequestReturnObj(
                request.param.get("status_code", 200),
                request.param.get("text", "MOCK_TEXT"),
            )
            with patch.object(requests, "post", return_value=return_value):
                import app  # pylint: disable=import-outside-toplevel

                app.app.config["TESTING"] = True
                with CustomClient(
                    app.app,
                    headers=request.param["headers"],
                    status_code=request.param["status_code"],
                ) as curr_client:
                    yield curr_client


@pytest.mark.parametrize(
    "client",
    [
        {
            "headers": {"AUTHORIZATION": "Bearer MOCK_AUTHORIZATION"},
            "verify_token_method": "verify_oauth2_token",
            "status_code": 200,
        },
        {
            "headers": {"AUTHORIZATION": "Bearer MOCK_AUTHORIZATION"},
            "verify_token_method": "verify_oauth2_token",
            "status_code": 401,
        },
        {
            "headers": {"AUTHORIZATION": "Bearer MOCK_AUTHORIZATION"},
            "verify_token_method": "verify_firebase_token",
            "status_code": 200,
        },
    ],
    indirect=True,
)
def test_root(client):  # pylint: disable=redefined-outer-name
    """Test root endpoint."""
    return_value = client.post(
        "/",
        query_string={},
    )
    parsed_url = urlparse(return_value.request.url)
    assert parsed_url.scheme == "http"
    assert parsed_url.netloc == "localhost"
    assert return_value.headers["Content-Type"] == "text/html; charset=utf-8"
    assert return_value.status_code == client.status_code
    for curr_response in return_value.response:
        assert curr_response.decode() == MockRequestReturnObj.text


def test_shutdown_handler(caplog):
    """Test shutdown_handler function."""

    def mock_signal_handler(*args, **kwargs):  # pylint: disable=unused-argument
        """Mock signal handler for testing shutdown handler."""

    with patch.dict(
        os.environ,
        {
            "BOT_USER": "MOCK_BOT_USER",
        },
    ):
        import app  # pylint: disable=import-outside-toplevel

        with caplog.at_level(app.gunicorn_logger.level):
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                app.shutdown_handler(signal.SIGINT, mock_signal_handler)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert "INFO" in caplog.text
    assert "Caught Signal Interrupt" in caplog.text


def raise_value_error(*args, **kwargs):
    """Function to patch id_token.verify_oauth2_token, to expliciylt test try-catch."""
    raise ValueError


@pytest.mark.parametrize(
    "headers,patch_kwargs",
    [
        ({}, {"return_value": None}),
        ({"Authorization": "DOES_NOT_START_WITH_BEARER"}, {"return_value": None}),
        ({"Authorization": "Bearer MOCK_AUTHORIZATION"}, {"return_value": None}),
        ({"Authorization": "Bearer MOCK_AUTHORIZATION"}, {"return_value": {}}),
        (
            {"Authorization": "Bearer MOCK_AUTHORIZATION"},
            {"return_value": {"email": "MOCK_EMAIL"}},
        ),
        ({"Authorization": "Bearer MOCK_AUTHORIZATION"}, {"new": raise_value_error}),
    ],
)
def test_rejection_modes(headers, patch_kwargs):
    """Tests to check the ways that the root endpoint can throw 403."""
    with patch.dict(
        os.environ,
        {
            "BOT_USER": "MOCK_BOT_USER",
        },
    ):
        import app  # pylint: disable=import-outside-toplevel

        with app.app.test_request_context(headers=headers):
            with pytest.raises(Forbidden) as pytest_wrapped_e:
                with patch.object(
                    id_token,
                    _DEFAULT_VERIFY_TOKEN_METHOD,
                    **patch_kwargs,
                ):
                    app.check_user_authentication()
    assert pytest_wrapped_e.value.response is None
    assert str(pytest_wrapped_e.value).startswith("403 Forbidden")
    assert pytest_wrapped_e.type == Forbidden
