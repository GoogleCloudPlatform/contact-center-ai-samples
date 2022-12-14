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

"""Unit tests frontend_blueprint.py."""

import os

import flask
import pytest
from frontend_blueprint import STATIC_FOLDER
from frontend_blueprint import frontend as blueprint
from mock import patch


def send_from_directory_mock(directory, filename):
    assert directory.endswith(STATIC_FOLDER)
    return filename


@pytest.fixture
def client():
    """Client fixture for testing a flask app."""

    with patch.object(flask, "send_from_directory", new=send_from_directory_mock):
        app = flask.Flask(__name__)
        app.register_blueprint(blueprint)

        app.config["TESTING"] = True
        with app.test_client() as curr_client:
            yield curr_client


def test_frontend_blueprint_no_path(client):
    return_value = client.get("/")
    for curr_response in return_value.response:
        assert curr_response.decode() == "index.html"


def test_frontend_blueprint(client):

    mock_path = "MOCK_PATH"

    with patch.object(os.path, "exists", return_value=True):
        return_value = client.get(f"/{mock_path}")
        for curr_response in return_value.response:
            assert curr_response.decode() == mock_path
