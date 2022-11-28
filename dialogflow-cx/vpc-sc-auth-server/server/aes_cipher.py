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


"""Encrypt and decrypt with AES."""


import base64
import uuid

from Crypto import Random
from Crypto.Cipher import AES


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
