# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test module for session.py."""

import os
from unittest import mock
from unittest.mock import Mock

import google.api_core.exceptions
import google.auth
from Crypto.PublicKey import RSA
from mock import patch


def test_session_create():
    """Test session.py:create"""

    def upload_from_file_mock(args):
        del args

    mock_blob = Mock()
    mock_blob.upload_from_file = upload_from_file_mock

    with patch.object(
        google.auth, "default", return_value=("MOCK_CREDENTIALS", "MOCK_PROJECT")
    ):
        import google.cloud.storage as storage  # pylint: disable=import-outside-toplevel,consider-using-from-import

        with patch.object(storage.blob, "Blob", return_value=mock_blob):
            import session  # pylint: disable=import-outside-toplevel

            private_key = RSA.generate(2048)
            public_key = private_key.publickey()
            public_pem = public_key.export_key().decode()
            session_id = "123456"
            with mock.patch.dict(os.environ, {"SESSION_BUCKET": "MOCK_SESSION_BUCKET"}):
                assert session.create({}, session_id=session_id, public_pem=public_pem)


def get_session_data(download_as_bytes_mock):
    """Use mocked fixtures to retrieve session data from read method."""
    mock_blob = Mock()
    mock_blob.download_as_bytes = download_as_bytes_mock

    with patch.object(
        google.auth, "default", return_value=("MOCK_CREDENTIALS", "MOCK_PROJECT")
    ):
        import google.cloud.storage as storage  # pylint: disable=import-outside-toplevel,consider-using-from-import

        with patch.object(storage.blob, "Blob", return_value=mock_blob):
            import session  # pylint: disable=import-outside-toplevel

            with mock.patch.dict(os.environ, {"SESSION_BUCKET": "MOCK_SESSION_BUCKET"}):
                return session.read("123456")


def test_session_read():
    """Test session.py:read"""
    mock_data = b"MOCK_DATA"

    def download_as_bytes_mock():
        return mock_data

    session_data = get_session_data(download_as_bytes_mock)
    assert len(session_data) == 2
    assert session_data["key"].getvalue() == mock_data
    assert session_data["session_data"].getvalue() == mock_data


def test_session_read_xfail():
    """Test session.py:read, expected to fail because of blob not found."""

    import session  # pylint: disable=import-outside-toplevel

    def download_as_bytes_mock():
        raise google.api_core.exceptions.NotFound(session.NOT_FOUND_ERROR_MESSAGE)

    session_data = get_session_data(download_as_bytes_mock)
    assert len(session_data) == 1
    assert session_data["error"].status == "401 UNAUTHORIZED"


def test_get_session_bucket_none():
    "Test additional code path where SESSION_BUCKET is not provided"
    import session  # pylint: disable=import-outside-toplevel

    try:
        session.get_session_bucket()
    except session.NoBucketError as exc:
        assert exc.message == session.NoBucketError.message
