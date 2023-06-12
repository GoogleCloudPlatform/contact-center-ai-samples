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

"""Test module for get_token.py."""

import json

import get_token
import pytest
import requests
from conftest import assert_response
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from google.oauth2 import id_token
from mock import mock_open, patch


@pytest.mark.hermetic
def test_lru_cache_bump_out(lru_fixture):
    """Test LruCache bumps LRU value out when over capacity."""
    (max_size, test_size) = (
        5,
        15,  # fmt: skip
    )
    for curr_val in range(test_size):
        assert lru_fixture(curr_val) == curr_val

    cache = get_token.LruCache(lru_fixture, max_size=max_size)
    for curr_val in range(max_size):
        assert cache(curr_val) == curr_val
    assert set(cache.cache.keys()) == {(val,) for val in range(max_size)}
    for curr_val in range(max_size, test_size):
        assert cache(curr_val) == curr_val
    assert set(cache.cache.keys()) == {
        (val,) for val in range(test_size - max_size, test_size)
    }


@pytest.mark.hermetic
def test_lru_cache_reuse(lru_fixture):
    """Test LruCache does cache lookup instead of retrieval."""
    mock_val = 10
    cache = get_token.LruCache(lru_fixture, max_size=1)
    first_val = cache(mock_val)
    second_val = cache(mock_val)
    assert first_val == second_val == mock_val
    assert len(cache.cache) == 1


@pytest.mark.integration
def test_get_token_from_auth_server_unknown_integration():
    """Integration test of get_token_from_auth_server against live auth service."""
    mock_session_id = "UNKNOWN_SESSION_ID"

    result = get_token.get_token_from_auth_server(mock_session_id)
    assert_response(result, 200, {"status": "BLOCKED", "reason": "REJECTED_REQUEST"})


@pytest.mark.hermetic
def test_get_token_from_auth_server_unknown_hermetic_401():
    """Integration test of get_token_from_auth_server against live auth service."""
    mock_session_id = "UNKNOWN_SESSION_ID"

    return_value = requests.Response()
    return_value.status_code = 401

    with patch.object(requests, "get", return_value=return_value):
        result = get_token.get_token_from_auth_server(mock_session_id)
    assert_response(result, 200, {"status": "BLOCKED", "reason": "REJECTED_REQUEST"})


@pytest.mark.hermetic
@patch.object(RSA, "import_key", return_value="MOCK_KEY")
@patch("builtins.open", mock_open(read_data="MOCK_DATE"))
def test_get_token_from_auth_server_decryption_error(
    mock_import_key,
    mock_zipfile,
):
    """Test get_token_from_auth_server, decryption error occurs."""

    class MockDecryptClass:  # pylint: disable=too-few-public-methods
        """Mock out class PKCS1_OAEP"""

        def decrypt(self, args):
            """Mock decrypt method."""
            del args
            raise ValueError

    with patch.object(requests, "get", return_value=mock_zipfile):
        with patch.object(PKCS1_OAEP, "new", return_value=MockDecryptClass()):
            result = get_token.get_token_from_auth_server("UNKNOWN_SESSION_ID")
    assert_response(result, 200, {"status": "BLOCKED", "reason": "DECRYPTION_ERROR"})
    mock_import_key.assert_called_once()


@pytest.mark.hermetic
def test_encryption_e2e():
    """Round-trip a plaintext message through AES/RSA."""

    plaintext = "Hello World"
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    public_pem = public_key.export_key().decode()
    private_pem = private_key.export_key().decode()
    aes_cipher = get_token.AESCipher()
    ciphertext = aes_cipher.encrypt(plaintext)

    # Instantiating PKCS1_OAEP object with the private key for decryption
    pu_key = RSA.import_key(public_pem)
    cipher = PKCS1_OAEP.new(key=pu_key)
    encrypted_message = cipher.encrypt(ciphertext)
    pr_key = RSA.import_key(private_pem)
    decrypt = PKCS1_OAEP.new(key=pr_key)
    decrypted_message = decrypt.decrypt(encrypted_message)
    assert aes_cipher.decrypt(decrypted_message).decode() == plaintext


@pytest.mark.hermetic
def test_get_token_from_auth_server_unknown_hermetic_200(mock_zipfile):
    """Hermetic test of get_token_from_auth_server."""
    mock_session_id = "UNKNOWN_SESSION_ID"

    class MockDecryptClass:  # pylint: disable=too-few-public-methods
        """Mock out class PKCS1_OAEP"""

        def decrypt(self, args):
            """Mock decrypt method."""
            del args
            return "MOCK_PLAINTEXT"

    mock_token_dict = {"MOCK_TOKEN_KEY": "MOCK_TOKEN_VAL"}

    with patch.object(requests, "get", return_value=mock_zipfile):
        with patch("builtins.open", mock_open(read_data="MOCK_DATE")) as mock_file:
            with patch.object(RSA, "import_key", return_value="MOCK_KEY"):
                with patch.object(PKCS1_OAEP, "new", return_value=MockDecryptClass()):
                    with patch.object(
                        get_token.AESCipher,
                        "decrypt",
                        return_value=json.dumps(mock_token_dict).encode(),
                    ):
                        result = get_token.get_token_from_auth_server(mock_session_id)
    mock_file.assert_called_with(get_token.PRIVATE_PEM_FILENAME, "r", encoding="utf8")
    assert len(result) == 1
    assert result["auth_data"] == mock_token_dict


@pytest.mark.hermetic
def test_get_token_no_session_id(mock_request):
    """Test get_token."""
    result = get_token.get_token(mock_request)
    assert_response(result, 200, {"status": "BLOCKED", "reason": "BAD_SESSION_ID"})


@pytest.mark.hermetic
@pytest.mark.parametrize("precache", [False, True])
def test_get_token_cached(mock_request, precache):
    """Test get_token when response is cached."""
    mock_session_id = "MOCK_SESSION_ID"
    mock_cache_response = {"response": {"MOCK_TOKEN_KEY": "MOCK_TOKEN_VAL"}}

    cache = get_token.LruCache(lambda _: mock_cache_response)
    if precache:
        cache.cache[mock_session_id] = mock_cache_response
    mock_request.cookies = {"session_id": mock_session_id}
    result = get_token.get_token(mock_request, cache=cache)
    assert result == mock_cache_response


@pytest.mark.hermetic
def test_get_token_failure_unknown(mock_request):
    """Test get_token with an unknown auth server error"""
    mock_session_id = "MOCK_SESSION_ID"
    mock_cache_response = {"auth_data": {"id_token": "MOCK_ID_TOKEN"}}
    cache = get_token.LruCache(lambda _: mock_cache_response)

    def mock_verify_oauth2_token_raise_unknown_error(token, request):
        del token
        del request
        raise ValueError("Unknown error")

    mock_request.cookies = {"session_id": mock_session_id}
    with patch.object(
        id_token,
        "verify_oauth2_token",
        new=mock_verify_oauth2_token_raise_unknown_error,
    ):
        result = get_token.get_token(mock_request, cache=cache)
    result = get_token.get_token(mock_request, cache=cache)
    assert_response(result, 200, {"status": "BLOCKED", "reason": "UNKNOWN"})


@pytest.mark.hermetic
def test_get_token_failure_expired(mock_request):
    """Test get_token with an expired token."""
    mock_session_id = "MOCK_SESSION_ID"
    mock_cache_response = {"auth_data": {"id_token": "MOCK_ID_TOKEN"}}
    cache = get_token.LruCache(lambda _: mock_cache_response)

    def mock_verify_oauth2_token_raise_value_error(token, request):
        del token
        del request
        raise ValueError("Token expired")

    mock_request.cookies = {"session_id": mock_session_id}
    with patch.object(
        id_token,
        "verify_oauth2_token",
        new=mock_verify_oauth2_token_raise_value_error,
    ):
        result = get_token.get_token(mock_request, cache=cache)
    assert_response(result, 200, {"status": "BLOCKED", "reason": "TOKEN_EXPIRED"})


@pytest.mark.hermetic
def test_get_token_failure_bad_email(mock_request):
    """Test get_token, with a bad email address."""
    mock_session_id = "MOCK_SESSION_ID"
    mock_cache_response = {"auth_data": {"id_token": "MOCK_ID_TOKEN"}}
    cache = get_token.LruCache(lambda _: mock_cache_response)

    def mock_verify_oauth2_token_raise_value_error(token, request):
        del token
        del request
        return {"email_verified": False}

    mock_request.cookies = {"session_id": mock_session_id}
    with patch.object(
        id_token,
        "verify_oauth2_token",
        new=mock_verify_oauth2_token_raise_value_error,
    ):
        result = get_token.get_token(mock_request, cache=cache)
    assert_response(result, 200, {"status": "BLOCKED", "reason": "BAD_EMAIL"})


@pytest.mark.hermetic
@pytest.mark.parametrize(
    "token_type,expected",
    [
        ("access_token", {"access_token": "MOCK_ACCESS_TOKEN"}),
        ("id_token", {"id_token": "MOCK_ID_TOKEN"}),
        ("email", {"email": "MOCK_EMAIL"}),
        ("UNKNOWN", None),
    ],
)
def test_get_token_failure_success(token_type, expected, mock_request):
    """Test get token for all token_types including an unknown type."""
    mock_session_id = "MOCK_SESSION_ID"
    mock_cache_response = {
        "auth_data": {
            "id_token": "MOCK_ID_TOKEN",
            "access_token": "MOCK_ACCESS_TOKEN",
            "email": "MOCK_EMAIL",
        }
    }
    cache = get_token.LruCache(lambda _: mock_cache_response)

    def mock_verify_oauth2_token(token, request):
        del token
        del request
        return {"email_verified": True}

    mock_request.cookies = {"session_id": mock_session_id}
    with patch.object(
        id_token,
        "verify_oauth2_token",
        new=mock_verify_oauth2_token,
    ):
        result = get_token.get_token(mock_request, cache=cache, token_type=token_type)

    if token_type != "UNKNOWN":
        assert len(result) == 1
        assert result == expected
    else:
        assert_response(
            result,
            200,
            {
                "status": "BLOCKED",
                "reason": (
                    'Requested token_type "UNKNOWN" not one of '
                    '["access_token","id_token","email"]'
                ),
            },
        )
