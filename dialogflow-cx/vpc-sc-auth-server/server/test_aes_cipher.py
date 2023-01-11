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


"""Test aes_cipher.py module."""


from aes_cipher import AESCipher
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def test_encryption_e2e():
    """Round-trip a plaintext message through AES/RSA."""

    plaintext = "Hello World"
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    public_pem = public_key.export_key().decode()
    private_pem = private_key.export_key().decode()
    aes_cipher = AESCipher()
    ciphertext = aes_cipher.encrypt(plaintext)

    # Instantiating PKCS1_OAEP object with the private key for decryption
    pu_key = RSA.import_key(public_pem)
    cipher = PKCS1_OAEP.new(key=pu_key)
    encrypted_message = cipher.encrypt(ciphertext)
    pr_key = RSA.import_key(private_pem)
    decrypt = PKCS1_OAEP.new(key=pr_key)
    decrypted_message = decrypt.decrypt(encrypted_message)
    assert aes_cipher.decrypt(decrypted_message).decode() == plaintext
