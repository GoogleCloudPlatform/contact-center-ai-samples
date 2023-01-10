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

"""Module to get a stored token from the VPC-SC Demo Auth Server."""


import base64
import collections
import io
import json
import logging
import uuid
import zipfile

import flask
import requests
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from google.auth.transport import requests as reqs
from google.oauth2 import id_token
from session_blueprint import AUTH_SERVICE_HOSTNAME

logger = logging.getLogger(__name__)
PRIVATE_PEM_FILENAME = "private_key.pem"


class LruCache:  # pylint: disable=too-few-public-methods
    """Quick implementation of an LRU cache."""

    def __init__(self, func, max_size=128):
        self.cache = collections.OrderedDict()
        self.func = func
        self.max_size = max_size

    def __call__(self, *args):
        cache = self.cache
        if args in cache:
            cache.move_to_end(args)
            return cache[args]
        result = self.func(*args)
        cache[args] = result
        if len(cache) > self.max_size:
            cache.popitem(last=False)
        return result


class AESCipher:
    """Organizes AES encryption methods."""

    def __init__(self, key=None, block_size=16):
        self.key = uuid.uuid4().hex.encode() if key is None else key
        self.block_size = block_size

    def pad(self, cstr):
        """Pad message if needed."""
        return cstr + (self.block_size - len(cstr) % self.block_size) * chr(
            self.block_size - len(cstr) % self.block_size
        )

    def unpad(self, cstr):
        """Unpad padded message."""
        return cstr[: -ord(cstr[len(cstr) - 1 :])]  # noqa: E203

    def encrypt(self, raw):
        """Encrypt plaintext."""
        raw = self.pad(raw).encode()
        init_vec = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, init_vec)
        return base64.b64encode(init_vec + cipher.encrypt(raw))

    def decrypt(self, enc):
        """Decrypt cyphertext."""
        enc = base64.b64decode(enc)
        init_vec = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, init_vec)
        return self.unpad(cipher.decrypt(enc[16:]))


def get_token_from_auth_server(session_id, auth_service_hostname=AUTH_SERVICE_HOSTNAME):
    """Retrieve a stored token from the VPC-SC Demo Auth Server."""

    auth_service_auth_endpoint = f"http://{auth_service_hostname}/auth"

    params = {
        "session_id": session_id,
    }

    req = requests.get(auth_service_auth_endpoint, params=params, timeout=10)
    if req.status_code == 401:
        logger.error(
            "  auth-service %s rejected request: %s",
            auth_service_auth_endpoint,
            req.text,
        )
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "REJECTED_REQUEST"}
                ),
            )
        }

    with open(PRIVATE_PEM_FILENAME, "r", encoding="utf8") as file_handle:
        private_pem = file_handle.read()

    with zipfile.ZipFile(io.BytesIO(req.content)) as zip_file:
        with zip_file.open("key") as curr_zip:
            key_bytes_stream = curr_zip.read()
        with zip_file.open("session_data") as curr_zip:
            session_data_bytes_stream = curr_zip.read()

    try:
        decrypt = PKCS1_OAEP.new(key=RSA.import_key(private_pem))
        decrypted_message = decrypt.decrypt(key_bytes_stream)
        aes_cipher = AESCipher(key=decrypted_message)
        return {
            "auth_data": json.loads(
                aes_cipher.decrypt(session_data_bytes_stream).decode()
            )
        }
    except ValueError as exc:
        logger.error("Decryption Error: %s", exc)
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps(
                    {"status": "BLOCKED", "reason": "DECRYPTION_ERROR"}
                ),
            )
        }


def get_token(
    request, token_type="access_token", cache=LruCache(get_token_from_auth_server)
):
    """Get a stored token from the VPC-SC Demo Auth Server, or from local cache."""

    if not request.cookies.get("session_id"):
        logger.info("get_token request did not have a session_id")
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps({"status": "BLOCKED", "reason": "BAD_SESSION_ID"}),
            )
        }

    session_id = request.cookies.get("session_id")

    response = cache(session_id)
    if "response" in response:
        cache.cache.pop(session_id, None)
        return response
    auth_data = response["auth_data"]

    try:
        info = id_token.verify_oauth2_token(auth_data["id_token"], reqs.Request())
    except ValueError as exc:
        if "Token expired" in str(exc):
            logger.info("  auth-service token expired")
            return {
                "response": flask.Response(
                    status=200,
                    response=json.dumps(
                        {"status": "BLOCKED", "reason": "TOKEN_EXPIRED"}
                    ),
                )
            }
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps({"status": "BLOCKED", "reason": "UNKNOWN"}),
            )
        }

    if not info["email_verified"]:
        logger.info("  oauth error: email not verified")
        return {
            "response": flask.Response(
                status=200,
                response=json.dumps({"status": "BLOCKED", "reason": "BAD_EMAIL"}),
            )
        }

    response = {}
    if token_type == "access_token":
        response["access_token"] = auth_data["access_token"]
    elif token_type == "id_token":
        response["id_token"] = auth_data["id_token"]
    elif token_type == "email":
        response["email"] = auth_data["email"]
    else:
        response = (
            f'  Requested token_type "{token_type}" not one of '
            '["access_token","id_token","email"]'
        )
        logger.info(response)
        response = {
            "response": flask.Response(
                status=200,
                response=json.dumps({"status": "BLOCKED", "reason": response.lstrip()}),
            )
        }
    return response
