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

"""Unit tests for utilities.py."""

from unittest.mock import Mock

import google_crc32c
import utilities
from google.cloud import secretmanager
from mock import patch

_MOCK_CORRUPT_CHECKSUM = "MOCK_CORRUPT_CHECKSUM"


class MockClient:  # pylint: disable=too-few-public-methods
    """Create a mock secretmanager.SecretManagerServiceClient class."""

    def __init__(self, mock_data, corrupt=False):
        self.mock_data = mock_data

        if not corrupt:
            crc32c = google_crc32c.Checksum()
            crc32c.update(self.mock_data)
            self.checksum = int(crc32c.hexdigest(), 16)
        else:
            self.checksum = _MOCK_CORRUPT_CHECKSUM

    def access_secret_version(self, **kwargs):
        """Implements access_secret_version interface for client class."""
        del kwargs
        return Mock(
            payload=Mock(
                data=self.mock_data,
                data_crc32c=self.checksum,
            )
        )


def get_mock_payload(mock_data, corrupt=False):
    """Get the payload from the function being tested, after configuring the mock."""

    with patch.object(
        secretmanager,
        "SecretManagerServiceClient",
        return_value=MockClient(mock_data, corrupt=corrupt),
    ):
        payload_response = utilities.access_secret_version(
            "MOCK_PROJECT_ID", "MOCK_SECRET_ID", "MOCK_VERSION_ID"
        )
        assert len(payload_response) == 2
        return payload_response


def test_access_secret_version():
    """Test utilities.access_secret_version with uncorrupted data."""
    mock_data = b"MOCK_DATA"
    payload_response = get_mock_payload(mock_data)
    assert payload_response["error"] is None
    assert payload_response["response"] == mock_data.decode()


def test_access_secret_version_corrupt():
    """Test utilities.access_secret_version with corrupted data (bad checksum)."""
    mock_data = b"MOCK_DATA"
    payload_response = get_mock_payload(mock_data, corrupt=True)
    assert payload_response["error"] == utilities.CORRUPTION_ERR_MSG
    assert payload_response["response"].payload.data == mock_data
    assert payload_response["response"].payload.data_crc32c == _MOCK_CORRUPT_CHECKSUM
