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

"""Module for testing analytics_utilities.py"""

import os

import analytics_utilities as au
import asset_utilities as asu
import get_token
import jsonschema
import pytest
import session_utilities as su
from conftest import MOCK_DOMAIN
from google.cloud import bigquery
from mock import patch


@patch.object(su, "user_service_domain", return_value=MOCK_DOMAIN)
def test_update_visit_cookie(mock_user_service_domain, mock_request, mock_response):
    """Test update_visit_cookie."""
    response = au.update_visit_cookie(mock_request, mock_response)
    mock_user_service_domain.assert_called_once()
    assert "visit_id" in response.headers["Set-Cookie"]


def test_actions():
    """Test that the ACTIONS maximum boundary makes sense."""
    assert len(au.ACTIONS) == au.SCHEMA["properties"]["action"]["maximum"] + 1


# pylint: disable=too-few-public-methods
class MockAction:
    """Mock analytics_utilities.ACTION Enum."""

    @property
    def value(self):
        """Mock python Enum value interface."""
        return "MOCK_ACTION"


class MockDataset:
    """Mock bigquery dataset object."""

    def table(self, database):
        """Mock bigquery table interface."""
        del database


class MockClient:
    """Class to mock bigquery client interface."""

    def __init__(self, insert_response):
        """Configure with response for insert_rows_json method."""
        self.insert_response = insert_response

    def dataset(self, name):
        """Mock dataset interface."""
        del name
        return MockDataset()

    def get_table(self, table_name):
        """Mock get_table interface."""
        del table_name

    def insert_rows_json(self, **kwargs):
        """Mock insert_rows_json interface."""
        del kwargs
        return self.insert_response


# pylint: enable=too-few-public-methods


@patch.dict(os.environ, {"ANALYTICS_DATABASE": "MOCK_DATABASE"})
@pytest.mark.parametrize(
    "data",
    [
        None,
        {},
        {"current_page": "MOCK_CURRENT_PATH"},
        {"MOCK_PROPERTY_KEY": "MOCK_PROPERTY_VALUE"},
    ],
)
@pytest.mark.parametrize(
    "cookies",
    [
        {"session_id": "MOCK_SESSION_ID"},
        {},
    ],
)
@pytest.mark.parametrize(
    "token_response",
    [
        {"response": "MOCK_RESPONSE"},
        {"email": "MOCK_EMAIL"},
    ],
)
@pytest.mark.parametrize(
    "mock_client_insert_response",
    [
        None,
        "MOCK_ERROR",
    ],
)
@patch.object(jsonschema, "validate", return_value=None)
@patch.object(asu, "get_credentials", return_value=None)
@patch.object(su, "user_service_domain", return_value=MOCK_DOMAIN)
def test_register_action(  # pylint: disable=too-many-arguments
    mock_user_service_domain,
    mock_get_credentials,
    mock_jsonschema,
    mock_request,
    mock_response,
    data,
    cookies,
    token_response,
    mock_client_insert_response,
):
    """Test register_action"""
    mock_request.cookies = cookies
    with patch.object(get_token, "get_token", return_value=token_response):
        with patch.object(
            bigquery, "Client", return_value=MockClient(mock_client_insert_response)
        ):
            response = au.register_action(
                mock_request,
                mock_response,
                MockAction(),
                data,
            )
    assert mock_user_service_domain.call_count >= 1
    mock_get_credentials.assert_called_once()
    mock_jsonschema.assert_called_once()
    assert response.status_code == 200


def test_validate_data_error(caplog):
    """Test validate_data, asserting that logging info is raised on a bad value."""
    au.validate_data({})
    assert len(caplog.records) == 1
    assert "Validation error:" in caplog.records[0].msg
