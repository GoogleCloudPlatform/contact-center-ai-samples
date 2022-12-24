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

"""Tests for update_utilities.py."""

import pytest
import requests
import status_utilities as su
import update_utilities as uu
from conftest import MockReturnObject
from google.cloud import storage
from google.oauth2 import credentials as oauth2_credentials
from mock import patch


@pytest.mark.parametrize(
    "restrict_access,status,expected",
    [
        (False, {"restrictedServices": ["MOCK_API"]}, []),
        (True, {"restrictedServices": []}, ["MOCK_API"]),
        (True, {}, ["MOCK_API"]),
    ],
)
def test_update_service_perimeter_status_inplace_success(
    restrict_access,
    status,
    expected,
):
    """Test update_service_perimeter_status_inplace, success cases."""
    service_perimeter_status = {"status": status}
    return_value = uu.update_service_perimeter_status_inplace(
        "MOCK_API",
        restrict_access,
        service_perimeter_status,
    )
    assert service_perimeter_status["status"]["restrictedServices"] == expected
    assert return_value is None


@pytest.mark.parametrize(
    "restrict_access,status",
    [
        (False, {"restrictedServices": []}),
        (False, {}),
        (True, {"restrictedServices": ["MOCK_API"]}),
    ],
)
def test_update_service_perimeter_status_inplace_misconfigured(
    restrict_access,
    status,
):
    """Test update_service_perimeter_status_inplace when misconfigured"""
    service_perimeter_status = {"status": status}
    return_value = uu.update_service_perimeter_status_inplace(
        "MOCK_API",
        restrict_access,
        service_perimeter_status,
    )
    assert return_value.status_code == 200
    assert return_value.response == []


def get_response():
    """Get a mock response from update_security_perimeter"""
    return uu.update_security_perimeter(
        "MOCK_TOKEN",
        "MOCK_API",
        False,
        "MOCK_PROJECT_ID",
        "MOCK_ACCESS_POLICY_NAME",
    )


@patch.object(su, "get_service_perimeter_status", return_value={"status": {}})
def test_update_security_perimeter_bad_status(mock_status):
    """Test /update_security_perimeter, bad service_perimeter_status"""
    return_value = get_response()
    mock_status.assert_called_once()
    assert return_value.status_code == 200
    assert return_value.response == []


@patch.object(su, "get_service_perimeter_status", return_value={"status": {}})
@patch.object(uu, "update_service_perimeter_status_inplace", return_value=None)
@patch.object(
    su, "get_service_perimeter_data_uri", return_value={"response": "MOCK_RESPONSE"}
)
def test_update_security_perimeter_uri_err(
    mock_get_service_perimeter_data_uri,
    mock_update_service_perimeter_status_inplace,
    mock_get_service_perimeter_status,
):
    """Test /update_security_perimeter, error in uri response."""
    return_value = get_response()
    assert return_value == {"response": "MOCK_RESPONSE"}
    mock_get_service_perimeter_data_uri.assert_called_once()
    mock_update_service_perimeter_status_inplace.assert_called_once()
    mock_get_service_perimeter_status.assert_called_once()


@patch.object(su, "get_service_perimeter_status", return_value={"status": {}})
@patch.object(uu, "update_service_perimeter_status_inplace", return_value=None)
@patch.object(su, "get_service_perimeter_data_uri", return_value={"uri": "MOCK_URI"})
@patch.object(requests, "patch", return_value=MockReturnObject(0, "MOCK_RESPONSE"))
def test_update_security_perimeter_bad_patch(
    mock_patch,
    mock_get_service_perimeter_data_uri,
    mock_update_service_perimeter_status_inplace,
    mock_get_service_perimeter_status,
):
    """Test /update_security_perimeter, bad patch."""
    return_value = get_response()
    assert return_value.status_code == 0
    for response in return_value.response:
        assert response.decode() == '"MOCK_RESPONSE"'
    mock_get_service_perimeter_data_uri.assert_called_once()
    mock_update_service_perimeter_status_inplace.assert_called_once()
    mock_get_service_perimeter_status.assert_called_once()
    mock_patch.assert_called_once()


@patch.object(su, "get_service_perimeter_status", return_value={"status": {}})
@patch.object(uu, "update_service_perimeter_status_inplace", return_value=None)
@patch.object(su, "get_service_perimeter_data_uri", return_value={"uri": "MOCK_URI"})
@patch.object(requests, "patch", return_value=MockReturnObject(200, "MOCK_RESPONSE"))
def test_update_security_perimeter_success(
    mock_patch,
    mock_get_service_perimeter_data_uri,
    mock_update_service_perimeter_status_inplace,
    mock_get_service_perimeter_status,
):
    """Test /update_security_perimeter, success."""
    return_value = get_response()
    assert return_value.status_code == 200
    assert return_value.response == []
    mock_get_service_perimeter_data_uri.assert_called_once()
    mock_update_service_perimeter_status_inplace.assert_called_once()
    mock_get_service_perimeter_status.assert_called_once()
    mock_patch.assert_called_once()


class MockClient:  # pylint: disable=too-few-public-methods
    """Mock storage.Client object."""

    def __init__(self, project, credentials):
        assert project == "MOCK_PROJECT"
        assert credentials == "MOCK_CREDENTIALS"

    def bucket(self, bucket):
        "Mock bucket interface."
        assert bucket == "MOCK_BUCKET"
        return "MOCK_BUCKET_OBJECT"


class MockBlob:  # pylint: disable=too-few-public-methods
    """Mock storage.blob.Blob object."""

    def __init__(self, filename, bucket_object):
        assert filename == "server.der"
        assert bucket_object == "MOCK_BUCKET_OBJECT"

    def download_as_string(self):
        "Mock download_as_string interface."
        return "MOCK_STRING"


@patch.object(oauth2_credentials, "Credentials", return_value="MOCK_CREDENTIALS")
@patch.object(storage, "Client", new=MockClient)
@patch.object(storage.blob, "Blob", new=MockBlob)
def test_get_cert(mock_credentials):
    """Test get_cert utility method."""
    assert uu.get_cert("MOCK_TOKEN", "MOCK_PROJECT", "MOCK_BUCKET") == "MOCK_STRING"
    mock_credentials.assert_called_once()
