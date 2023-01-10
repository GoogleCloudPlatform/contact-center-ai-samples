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

"""conftest module for pytest containing test classes for reuse."""

import io
import json
import zipfile
from urllib.parse import urlparse

import flask
import pytest
import requests
from werkzeug.test import EnvironBuilder

MOCK_DOMAIN = "MOCK_DOMAIN."


class MockReturnObject:  # pylint: disable=too-few-public-methods
    """Class to mock out json interface of requests.Response."""

    def __init__(self, status_code, data=None, text=None):
        self.status_code = status_code
        self.data = {} if data is None else data
        self._text = text

    def json(self):
        """Mock json interface."""
        return self.data

    @property
    def text(self):
        """Mock text interface; fall back to json as string."""
        if self._text is None:
            return json.dumps(self.data)
        return self._text


def assert_response(result, status_code, expected):
    """Assert propertes of result response."""
    assert len(result) == 1
    response = result["response"]
    assert response.status_code == status_code
    assert len(response.response) == 1
    assert json.loads(response.response[0].decode()) == expected


def assert_response_ep(
    return_value, status_code, endpoint, response=None, netloc=MOCK_DOMAIN
):
    """Assert function for testing responses"""
    parsed_url = urlparse(return_value.request.url)
    assert return_value.headers["Content-Type"] == "text/html; charset=utf-8"
    assert parsed_url.scheme == "https"
    assert parsed_url.netloc == netloc
    assert parsed_url.path == endpoint
    assert return_value.status_code == status_code
    if response is not None:
        for curr_response in return_value.response:
            assert curr_response.decode() == response


@pytest.fixture
def lru_fixture():
    """Fixture function for testing LruCache."""
    return lambda x: x


@pytest.fixture(scope="function")
def app(request):
    """Fixture for tests on session blueprint."""
    curr_app = flask.Flask(__name__)
    curr_app.register_blueprint(request.param)
    curr_app.config["TESTING"] = True
    return curr_app


@pytest.fixture
def mock_request():
    """Mock request for testing functions that take a request as an arg."""
    builder = EnvironBuilder()
    return builder.get_request()


@pytest.fixture
def mock_response():
    """Mock request for testing functions that take a request as an arg."""
    return flask.Response()


def generate_mock_register_action():
    """Factory function to provide a MockRegisterAction fixture."""

    class MockRegisterAction:
        """Mock Register action function with call counter."""

        def __init__(self):
            self.called_counter = 0

        def __call__(self, request, response, action, data=None):
            self.called_counter += 1
            del request
            del action
            del data
            return response

        def assert_called_once(self):
            """Method to ensure that the mock fixture is envoked once."""
            assert self.called_counter == 1

    return MockRegisterAction()


@pytest.fixture
def mock_zipfile():
    """Create a mock zipfile"""
    return_value = requests.Response()
    return_value.status_code = 200
    return_value.raw = io.BytesIO()
    with zipfile.ZipFile(return_value.raw, "w") as zip_file:
        zip_file.writestr("key", "MOCK_KEY")
        zip_file.writestr("session_data", "MOCK_SESSION_DATA")
    return_value.raw.seek(0)
    return return_value
