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

"""Unit tests for create_keys.py."""

from unittest import mock
from unittest.mock import mock_open, patch

import create_keys
import pytest
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


@pytest.mark.hermetic
def test_generate_key_pair():
    """Test key pair generation."""

    plaintext = "MOCK_PLAINTEXT"

    with patch("create_keys.open", mock_open()) as mocked_file:
        create_keys.generate_key_pair()

    assert mocked_file.mock_calls[0] == mock.call(
        "private_key.pem", "w", encoding="utf-8"
    )
    for name, args, _ in mocked_file.mock_calls:
        if name == "().write":
            if "PUBLIC" in args[0]:
                public_pem = args[0]
            if "PRIVATE" in args[0]:
                private_pem = args[0]

    pu_key = RSA.import_key(public_pem)
    cipher = PKCS1_OAEP.new(key=pu_key)
    encrypted_message = cipher.encrypt(plaintext.encode())

    pr_key = RSA.import_key(private_pem)
    decrypt = PKCS1_OAEP.new(key=pr_key)
    decrypted_message = decrypt.decrypt(encrypted_message)

    assert decrypted_message.decode() == plaintext
