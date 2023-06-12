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

"""
    Stored session management.
    Based on https://github.com/GoogleCloudPlatform/emblem/blob/main/website/middleware/session.py

    Create and read data for a stored session.

    Examples:
        from middleware import session

        session_id = session.create({"name": "J. Doe", "email": "jdoe@example.com"})

        info = session.read(session_id)
        info["country"] = "US"

    Implementation:

    The session data will be stored in Google Cloud Storage. A bucket must already
    exist for this use, and the name of the bucket provided in the environment
    variable SESSION_BUCKET. The website should be using a service
    account that has object read and write permission in the bucket. Access to
    the bucket and its contents should be tightly controlled.

    No other objects should be in this bucket as they might conflict with
    the objects managed by this module.

    The code that calls these methods is responsible for managing
    a cookie with the session ID in the user's web browser.
"""


import io
import json
import logging
import os

import google.api_core.exceptions
import google.auth
import google.cloud.storage as storage  # pylint: disable=consider-using-from-import
from aes_cipher import AESCipher
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from flask import Response

log = logging.getLogger("session")
credentials, project = google.auth.default()

NOT_FOUND_ERROR_MESSAGE = "Exception: google.api_core.exceptions.NotFound"


class NoBucketError(Exception):
    """Exception to throw when environment does not have SESSION_BUCKET set."""

    message = "Environment variable SESSION_BUCKET is required"

    def __init__(self):
        """Initialize NoBucketError with default message"""


def get_session_bucket():
    """# Initialize data that's not specific to an http request."""
    session_bucket_name = os.environ.get("SESSION_BUCKET")
    if session_bucket_name is None:
        log.error("Could not initialize session module.")
        raise NoBucketError()
    return storage.Client().bucket(session_bucket_name)


def create(session_data, session_id=None, public_pem=None):
    """Create a stored session containing the provided data.

    Args:
        session_data: the data to be saved for this session. It can be any data
            type that can be serialized and then deserialized with the Python
            standard json module.

    Returns:
        A string containing an identifier for the created session, or None if
        the session store was not created.
    """

    bucket = get_session_bucket()

    aes_cipher = AESCipher()
    rsa_cipher = PKCS1_OAEP.new(key=RSA.import_key(public_pem))

    aes_key_ciphertext = rsa_cipher.encrypt(aes_cipher.key)
    ciphertext = aes_cipher.encrypt(json.dumps(session_data))

    blob = storage.blob.Blob(f"{session_id}.key", bucket)
    stream = io.BytesIO(aes_key_ciphertext)
    blob.upload_from_file(stream)

    blob = storage.blob.Blob(f"{session_id}.aes", bucket)
    stream = io.BytesIO(ciphertext)
    blob.upload_from_file(stream)

    return session_id


def read(session_id):
    """Return the data previously saved for the specified session id.

    Args:
        session_id (str): the unique identifier of the session store.

    Returns:
        The stored session data if it exists and can be retrieved,
        None otherwise.
    """

    bucket = get_session_bucket()

    try:
        blob = storage.blob.Blob(f"{session_id}.key", bucket)
        key_bytes = blob.download_as_bytes()
        blob = storage.blob.Blob(f"{session_id}.aes", bucket)
        session_data_bytes = blob.download_as_bytes()
        return {
            "key": io.BytesIO(key_bytes),
            "session_data": io.BytesIO(session_data_bytes),
        }
    except google.api_core.exceptions.NotFound:
        return {"error": Response(status=401, response=NOT_FOUND_ERROR_MESSAGE)}
