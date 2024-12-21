from __future__ import annotations
import base64
import os
import json
import time
from enum import Enum
from dataclasses import dataclass

import keyring
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from utils import safe_json_loads
from consts import APP_NAME

"""
Exceptions
"""
class AESGCMCipherNotInitializedError(Exception):
    """AESGCMCipher is not initialized."""
    pass

class RSACipherNotInitializedError(Exception):
    """RSACipher is not initialized."""
    pass

class InvalidSecureStorageKeyError(Exception):
    """Invalid secure storage key."""
    pass

class IllegalAESGCMCipherAccessError(Exception):
    """
    Illegal AESGCMCipher access.
    Only accessible through `_get_password`
    `_set_password` and/or `_delete_password`.
    """
    pass

"""
Enums, Types
"""
class SecureStorageKey(str, Enum):
    AESGCM_CIPHER_KEY = "aesgcm_cipher_key"
    AESGCM_CIPHER_KEY_BACKUP = "aesgcm_cipher_key_backup"
    PUBLIC_PEM = "public_pem"
    PRIVATE_PEM = "private_pem"
    ACCOUNTS = "accounts"

    @classmethod
    def keys(cls) -> list[str]:
        return [key.value for key in cls]

    def __str__(self) -> str:
        return self.value

"""
Constants
"""
SECURE_STORAGE_KEY_LIST = SecureStorageKey.keys()
CACHE_TTL = 1800
ROTATE_KEY_TTL = 86400

class SecureStorage:
    _instance = None
    _cache: SecureStorageCache = None
    _encryptor: AESGCMCipher = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._cache = SecureStorageCache()
            cls._instance._init_aesgcm_cipher()
            cls._instance._init_rsa_cipher()

        return cls._instance

    def __del__(self):
        self.clear()

    def _wrap_with_timestamp(self, key_value: str) -> str:
        return json.dumps({
            "created_at": time.time(),
            "value": key_value
        })

    def _parse_key_value(self, key_value: str) -> tuple[any, float | None]:
        key_value = safe_json_loads(key_value)

        if isinstance(key_value, dict) and "created_at" in key_value and "value" in key_value:
            return key_value["value"], key_value["created_at"]

        return key_value, None

    def _check_key(self, key: str | SecureStorageKey) -> None:
        if str(key) not in SECURE_STORAGE_KEY_LIST:
            raise InvalidSecureStorageKeyError

    def _get_password(self, key: SecureStorageKey) -> str:
        self._check_key(key)
        return keyring.get_password(APP_NAME, key)

    def _set_password(self, key: SecureStorageKey, value: str) -> None:
        self._check_key(key)
        keyring.set_password(APP_NAME, key, value)

    def _delete_password(self, key: SecureStorageKey) -> None:
        self._check_key(key)
        keyring.delete_password(APP_NAME, key)

    def _init_aesgcm_cipher(self) -> bytes:
        key = self._get_password(SecureStorageKey.AESGCM_CIPHER_KEY)
        if not key:
            key = os.urandom(32).hex()
            self._set_password(SecureStorageKey.AESGCM_CIPHER_KEY, self._wrap_with_timestamp(key))
            self._encryptor = AESGCMCipher(bytes.fromhex(key))
        else:
            key = self._parse_key_value(key)
            if len(key) == 2 and key[1] + ROTATE_KEY_TTL < time.time():
                self.clear()
                self._rotate_aesgcm_cipher()

    def _rotate_aesgcm_cipher(self) -> None:
        temp_store = {}
        for key in SECURE_STORAGE_KEY_LIST:
            key_value = self.get_key_value(key)
            if key_value:
                temp_store[key] = key_value

        aesgcm_cipher_key_backup = self._get_password(SecureStorageKey.AESGCM_CIPHER_KEY)
        self._set_password(SecureStorageKey.AESGCM_CIPHER_KEY_BACKUP, aesgcm_cipher_key_backup)

        try:
            self._delete_password(SecureStorageKey.AESGCM_CIPHER_KEY)
            self._init_aesgcm_cipher()
            for key, value in temp_store.items():
                self.add_key(key, value)
        except Exception as e:
            # Restore the AESGCM cipher key if the rotation fails
            self._set_password(SecureStorageKey.AESGCM_CIPHER_KEY, aesgcm_cipher_key_backup)
            self._init_aesgcm_cipher()
            for key, value in temp_store.items():
                self.add_key(key, value)

            raise e

    def _init_rsa_cipher(self) -> None:
        is_private_pem_set = bool(self._get_password(SecureStorageKey.PRIVATE_PEM))
        is_public_pem_set = bool(self._get_password(SecureStorageKey.PUBLIC_PEM))

        if not is_private_pem_set or not is_public_pem_set:
            rsa_cipher = RSACipher()
            self.add_key(SecureStorageKey.PRIVATE_PEM, self._wrap_with_timestamp(rsa_cipher.get_private_pem()))
            self.add_key(SecureStorageKey.PUBLIC_PEM, self._wrap_with_timestamp(rsa_cipher.get_public_pem()))

    def get_key_value(self,
        key_name: SecureStorageKey,
        associated_data: bytes = None,
        decrypt: bool = True
    ) -> any:
        if key_name in [SecureStorageKey.AESGCM_CIPHER_KEY, SecureStorageKey.AESGCM_CIPHER_KEY_BACKUP]:
            raise IllegalAESGCMCipherAccessError

        self._check_key(key_name)

        key_value = self._cache.get(key_name)
        if not key_value:
            key_value = self._get_password(key_name)
            if not key_value:
                return None
            self._cache.set(key_name, key_value)

        if decrypt:
            if self._encryptor:
                key_value = self._encryptor.decrypt(key_value, associated_data)
                key_value = self._parse_key_value(key_value)[0]
            else:
                raise AESGCMCipherNotInitializedError

        return key_value

    def add_key(self,
        key_name: SecureStorageKey,
        key_value: any,
        associated_data: bytes = None
    ) -> None:
        if key_name in [SecureStorageKey.AESGCM_CIPHER_KEY, SecureStorageKey.AESGCM_CIPHER_KEY_BACKUP]:
            raise IllegalAESGCMCipherAccessError

        self._check_key(key_name)

        key_value = json.dumps(key_value)
        if not self._encryptor:
            raise AESGCMCipherNotInitializedError

        key_value = self._encryptor.encrypt(key_value, associated_data)
        self._set_password(key_name, key_value)
        self._cache.set(key_name, key_value)

    def delete_key(self, key_name: SecureStorageKey) -> None:
        if key_name in [SecureStorageKey.AESGCM_CIPHER_KEY, SecureStorageKey.AESGCM_CIPHER_KEY_BACKUP]:
            raise IllegalAESGCMCipherAccessError

        self._delete_password(key_name)
        self._cache.delete(key_name)

    def clear(self) -> None:
        self._cache.destroy()

    def destroy(self) -> None:
        if self._cache:
            self._cache.destroy()

        try:
            for key in SECURE_STORAGE_KEY_LIST:
                self._delete_password(key)
        except keyring.errors.PasswordDeleteError:
            print("Failed to delete keyring password.")
            pass

class SecureStorageCache:
    @dataclass
    class StoreData:
        value: any
        timestamp: float

        def is_expired(self) -> bool:
            return time.time() - self.timestamp > CACHE_TTL

    _instance = None
    _store: dict[str, StoreData]

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._store = {}

        return cls._instance

    def __del__(self):
        self.destroy()

    def get(self, key: str) -> any:
        if key not in self._store:
            return None

        store_data: SecureStorageCache.StoreData = self._store[key]
        if store_data.is_expired():
            self.delete(key)

        return store_data.value

    def set(self, key: str, value: any):
        self._store[key] = SecureStorageCache.StoreData(value, time.time())

    def delete(self, key: str):
        if key in self._store:
            random_bytes = os.urandom(len(str(self._store[key])))
            self._store[key] = random_bytes.hex()
            del self._store[key]

    def destroy(self):
        for key in list(self._store.keys()):
            self.delete(key)

        self._store = {}

class AESGCMCipher:
    def __init__(self, key: bytes):
        if len(key) not in [16, 24, 32]:
            raise ValueError("Key length must be 16, 24, or 32 bytes.")

        try:
            self._cipher = AESGCM(key)
        finally:
            random_bytes = os.urandom(len(str(key)))
            key = random_bytes.hex()

    def encrypt(self, plain_text: str, associated_data: bytes = None) -> str:
        nonce = os.urandom(12)
        cipher_text = self._cipher.encrypt(nonce, plain_text.encode(), associated_data)
        return base64.b64encode(nonce + cipher_text).decode('utf-8')

    def decrypt(self, encrypted_text: str, associated_data: bytes = None) -> str:
        encrypted_text = base64.b64decode(encrypted_text)
        nonce = encrypted_text[:12]
        cipher_text = encrypted_text[12:]
        return self._cipher.decrypt(nonce, cipher_text, associated_data).decode('utf-8')

class RSACipher:
    def __init__(self):
        self._create_private_key()
        self._create_public_key()

    def _create_private_key(self):
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self._private_pem = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def _create_public_key(self):
        if not self._private_key:
            raise RSACipherNotInitializedError

        self._public_key = self._private_key.public_key()
        self._public_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def get_public_pem(self) -> str:
        return self._public_pem.decode("utf-8") if isinstance(self._public_pem, bytes) else self._public_pem

    def get_private_pem(self) -> str:
        return self._private_pem.decode("utf-8") if isinstance(self._private_pem, bytes) else self._private_pem

    @staticmethod
    def decrypt_password(
        encrypted_b64_password: str,
        private_pem: str | bytes
    ) -> str:
        if isinstance(private_pem, str):
            private_pem = private_pem.encode('utf-8')

        private_key = serialization.load_pem_private_key(private_pem, password=None)
        return private_key.decrypt(
            base64.b64decode(encrypted_b64_password),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode("utf-8")

__all__ = [
    "SecureStorage",
    "SecureStorageKey",
    "AESGCMCipher",
    "RSACipher",
    "RSACipherNotInitializedError",
    "AESGCMCipherNotInitializedError",
    "InvalidSecureStorageKeyError",
    "IllegalAESGCMCipherAccessError"
]
