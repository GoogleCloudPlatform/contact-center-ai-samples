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

import pytest
from mock import mock_open, patch
from session_blueprint import PUBLIC_PEM_FILENAME
from session_blueprint import session as blueprint


@pytest.mark.hermetic
@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
def test_session_route(app):
    """Test /session."""
    mock_domain = "MOCK_DOMAIN."
    endpoint = "/session"
    with patch.dict(os.environ, {"PROD": "true"}):
        with app.test_client() as curr_client:
            with patch("builtins.open", mock_open(read_data="MOCK_DATE")) as mock_file:
                return_value = curr_client.get(
                    endpoint, base_url=f"https://{mock_domain}"
                )

    mock_file.assert_called_with(PUBLIC_PEM_FILENAME, "r", encoding="utf8")
    parsed_url = urlparse(return_value.request.url)
    cookie_list = sorted(return_value.headers.getlist("Set-Cookie"))
    assert cookie_list[0].startswith("session_id=")
    assert cookie_list[1].startswith("user_logged_in=true")
    assert return_value.headers["Content-Type"] == "text/html; charset=utf-8"
    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == mock_domain
    assert parsed_url.path == endpoint
    assert return_value.status_code == 302


@pytest.mark.hermetic
@pytest.mark.parametrize("app", [blueprint], indirect=["app"])
def test_logout_route(app):
    """Test /logout"""
    mock_domain = "MOCK_DOMAIN."
    endpoint = "/logout"
    with patch.dict(os.environ, {"PROD": "true"}):
        with app.test_client() as curr_client:
            curr_client.set_cookie(mock_domain, "session_id", "MOCK_SESSION_ID")
            curr_client.set_cookie(mock_domain, "user_logged_in", "MOCK_SESSION_ID")
            return_value = curr_client.get(endpoint, base_url=f"https://{mock_domain}")
    parsed_url = urlparse(return_value.request.url)
    cookie_list = sorted(return_value.headers.getlist("Set-Cookie"))
    assert cookie_list[0].startswith("session_id=;")
    assert r"Expires=Thu, 01 Jan 1970 00:00:00 GMT" in cookie_list[0]
    assert cookie_list[1].startswith("user_logged_in=;")
    assert r"Expires=Thu, 01 Jan 1970 00:00:00 GMT" in cookie_list[1]
    assert return_value.headers["Content-Type"] == "text/html; charset=utf-8"
    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == mock_domain
    assert parsed_url.path == endpoint
    assert return_value.status_code == 302
