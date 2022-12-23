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

import json
from urllib.parse import urlparse

import flask
import pytest

MOCK_DOMAIN = "MOCK_DOMAIN."


class MockReturnObject:  # pylint: disable=too-few-public-methods
    """Class to mock out json interface of requests.Response."""

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        """Mock json interface."""
        return self.data

    @property
    def text(self):
        """Mock text attribute interface."""
        return json.dumps(self.data)


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


@pytest.fixture(scope='function')
def app(request):
    """Fixture for tests on session blueprint."""
    curr_app = flask.Flask(__name__)
    curr_app.register_blueprint(request.param)
    curr_app.config["TESTING"] = True
    return curr_app