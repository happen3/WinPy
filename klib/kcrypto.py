import hashlib
import os
import sys

from cryptography.hazmat.primitives import padding

sys.path.append("..\\mlibs")
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class Crypto:
    @staticmethod
    def hash(method: str, data: bytes) -> bytes:
        match method.lower():
            case "md5":
                return hashlib.md5(data).hexdigest().encode()
            case "sha1":
                return hashlib.sha1(data).hexdigest().encode()
            case "sha224":
                return hashlib.sha224(data).hexdigest().encode()
            case "sha256":
                return hashlib.sha256(data).hexdigest().encode()
            case "sha384":
                return hashlib.sha384(data).hexdigest().encode()
            case "sha512":
                return hashlib.sha512(data).hexdigest().encode()
            case "blake2b":
                return hashlib.blake2b(data).hexdigest().encode()
            case "blake2s":
                return hashlib.blake2s(data).hexdigest().encode()

    @staticmethod
    def generate_salt(salt_size: int) -> bytes:
        salt = os.urandom(salt_size)
        return salt

    @staticmethod
    def salt(salt: bytes, khash: bytes) -> bytes:
        return salt + khash

    @staticmethod
    def kaes(data: bytes, key: bytes):    # Generate a random initialization vector (IV)
        iv = os.urandom(16)

        # Create AES cipher object with CBC mode and random IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Pad the plaintext to be a multiple of 16 bytes (AES block size)
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_plaintext = padder.update(data) + padder.finalize()

        # Encrypt the padded plaintext
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        return iv, ciphertext

    @staticmethod
    def kaes_decrypt(key: bytes, iv: bytes, ciphertext: bytes):
        # Create AES cipher object with CBC mode and given IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the ciphertext
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad the plaintext
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext


if __name__ == '__main__':
    print("MD5 of 'Hello, World':", Crypto.hash("MD5", b"Hello, World!").decode())
    print("Salted hash (SHA512) of 'Hello, World!':", Crypto.salt(Crypto.generate_salt(8),
                                                                  Crypto.hash("SHA512", b"Hello, World!")))
    print("AES of 'Hello, World!':", Crypto.kaes(b"Hello, World!", os.urandom(32)))
