from __future__ import annotations
import base64
import os
import json
import time
from enum import Enum
from typing import TypedDict

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
    # Standard Keys
    AESGCMCipherKey = "aesgcm_cipher_key"
    AESGCMCipherKeyBackup = "aesgcm_cipher_key_backup"
    PublicPem = "public_pem"
    PrivatePem = "private_pem"
    PublicPemBackup = "public_pem_backup"
    PrivatePemBackup = "private_pem_backup"

    # Custom Keys
    Accounts = "accounts"

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
ROTATE_FAILURE_TTL = ROTATE_KEY_TTL / 2

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
            for key in SECURE_STORAGE_KEY_LIST:
                try:
                    if key in [
                        SecureStorageKey.AESGCMCipherKey,
                        SecureStorageKey.AESGCMCipherKeyBackup,
                    ]:
                        continue

                    print("key:", key)
                    print("value:", cls._instance.get_key_value(key))
                except keyring.errors.PasswordDeleteError:
                    print(f"`{key}` could not found in keyring to delete. Skipping...")
                    pass

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
            raise InvalidSecureStorageKeyError(f"Invalid secure storage key: {key}")

    def _get_password(self, key: SecureStorageKey) -> str | None:
        self._check_key(key)
        return keyring.get_password(APP_NAME, key)

    def _set_password(self, key: SecureStorageKey, value: str) -> None:
        self._check_key(key)
        keyring.set_password(APP_NAME, key, value)

    def _delete_password(self, key: SecureStorageKey) -> None:
        self._check_key(key)
        keyring.delete_password(APP_NAME, key)

    def _init_aesgcm_cipher(self) -> bytes:
        key = self._get_password(SecureStorageKey.AESGCMCipherKey)
        if not key:
            key = os.urandom(32).hex()
            self._set_password(SecureStorageKey.AESGCMCipherKey, self._wrap_with_timestamp(key))
            self._encryptor = AESGCMCipher(bytes.fromhex(key))
        else:
            key = self._parse_key_value(key)
            self._encryptor = AESGCMCipher(bytes.fromhex(key[0]))
            if key[1] and key[1] + ROTATE_KEY_TTL < time.time():
                self._rotate_aesgcm_cipher()

    def _rotate_aesgcm_cipher(self) -> None:
        print("Rotating AESGCM cipher...")
        self.clear()

        temp_store = {}
        for key in SECURE_STORAGE_KEY_LIST:
            if key in [
                SecureStorageKey.AESGCMCipherKey,
                SecureStorageKey.AESGCMCipherKeyBackup,
            ]:
                continue

            try:
                key_value = self.get_key_value(key, use_cache=False)
                if key_value:
                    temp_store[key] = key_value
            except Exception as e:
                print(f"`{key}` value could not be retrieved. Skipping...")

        aesgcm_cipher_key_backup = self._get_password(SecureStorageKey.AESGCMCipherKey)
        self._set_password(SecureStorageKey.AESGCMCipherKeyBackup, aesgcm_cipher_key_backup)

        try:
            self._delete_password(SecureStorageKey.AESGCMCipherKey)
            self._init_aesgcm_cipher()
            for key, value in temp_store.items():
                self.add_key(key, value)

            print("AESGCM cipher rotation completed successfully.")
        except Exception as e:
            print("Rotation failed. Restoring AESGCM cipher key...",)

            aesgcm_cipher_key_backup = self._parse_key_value(aesgcm_cipher_key_backup)
            aesgcm_cipher_key_backup[1] = time.time() - ROTATE_FAILURE_TTL
            self._set_password(SecureStorageKey.AESGCMCipherKey, aesgcm_cipher_key_backup)
            self._init_aesgcm_cipher()
            for key, value in temp_store.items():
                self.add_key(key, value)

            print("AESGCM cipher rotation completed unsuccessfully.")
            raise e
        finally:
            for key in temp_store.keys():
                temp_store[key] = None
            del temp_store

    def _init_rsa_cipher(self) -> None:
        is_private_pem_set = bool(keyring.get_password(APP_NAME, SecureStorageKey.PrivatePem))
        is_public_pem_set = bool(keyring.get_password(APP_NAME, SecureStorageKey.PublicPem))

        if not is_private_pem_set or not is_public_pem_set:
            rsa_cipher = RSACipher()
            self.add_key(SecureStorageKey.PrivatePem, rsa_cipher.get_private_pem())
            self.add_key(SecureStorageKey.PublicPem, rsa_cipher.get_public_pem())

    """def _init_rsa_cipher(self) -> None:
        private_pem = self._get_password(SecureStorageKey.PrivatePem)
        public_pem = self._get_password(SecureStorageKey.PublicPem)
        if not private_pem or not public_pem:
            rsa_cipher = RSACipher()
            self.add_key(SecureStorageKey.PrivatePem, self._wrap_with_timestamp(rsa_cipher.get_private_pem()))
            self.add_key(SecureStorageKey.PublicPem, self._wrap_with_timestamp(rsa_cipher.get_public_pem()))
        else:
            private_pem = self._parse_key_value(private_pem)
            public_pem = self._parse_key_value(public_pem)
            if len(private_pem) == 2 and private_pem[1] + ROTATE_KEY_TTL < time.time():
                self._rotate_rsa_cipher()
            elif len(public_pem) == 2 and public_pem[1] + ROTATE_KEY_TTL < time.time():
                self._rotate_rsa_cipher()"""

    """def _rotate_rsa_cipher(self) -> None:
        # TODO: Önce AESGCM test edilsin ardından buraya dönülür ve
        # TODO: encrypted password çekilmeli key_value dan belki key_value lara bir meta data dict
        # TODO: eklenebilir aynı created_at wrap with timestamp gibi. ama önce aesgcm test edilsin
        # TODO: ve buradaki temp_store çıktısı nedir bir ona bakılsın.
        self.clear()

        temp_store = {}
        for key in SECURE_STORAGE_KEY_LIST:
            if key in [
                SecureStorageKey.PrivatePem,
                SecureStorageKey.PublicPem,
                SecureStorageKey.PrivatePemBackup,
                SecureStorageKey.PublicPemBackup
            ]:
                continue

            key_value = self.get_key_value(key)
            if key_value:
                temp_store[key] = key_value

        private_pem_backup = self.get_key_value(SecureStorageKey.PrivatePem)
        self.add_key(SecureStorageKey.PrivatePemBackup, private_pem_backup)
        public_pem_backup = self.get_key_value(SecureStorageKey.PublicPem)
        self.add_key(SecureStorageKey.PublicPemBackup, public_pem_backup)"""

    def get_key_value(self,
        key_name: SecureStorageKey,
        associated_data: bytes = None,
        decrypt: bool = True,
        use_cache: bool = True
    ) -> any:
        if key_name in [SecureStorageKey.AESGCMCipherKey, SecureStorageKey.AESGCMCipherKeyBackup]:
            raise IllegalAESGCMCipherAccessError

        self._check_key(key_name)
        print(f"Getting key value...: {key_name}")
        key_value = self._cache.get(key_name) if use_cache else None
        if not key_value:
            key_value = self._get_password(key_name)
            print(f"get_key_value: {key_value}")
            if not key_value:
                return None
            if use_cache: self._cache.set(key_name, key_value)

        if decrypt:
            if self._encryptor:
                key_value = self._encryptor.decrypt(key_value, associated_data)
                key_value = self._parse_key_value(key_value)[0]
            else:
                raise AESGCMCipherNotInitializedError
        print(f"Decrypted get_key_value: {key_value}")
        return key_value

    def add_key(self,
        key_name: SecureStorageKey,
        key_value: any,
        associated_data: bytes = None
    ) -> None:
        if key_name in [SecureStorageKey.AESGCMCipherKey, SecureStorageKey.AESGCMCipherKeyBackup]:
            raise IllegalAESGCMCipherAccessError

        self._check_key(key_name)

        key_value = json.dumps(key_value)
        if not self._encryptor:
            raise AESGCMCipherNotInitializedError
        print(f"Encrypting...: key_name: {key_name}, key_value: {key_value}, cipher_key: {self._get_password(SecureStorageKey.AESGCMCipherKey)}")
        key_value = self._encryptor.encrypt(key_value, associated_data)
        self._set_password(key_name, key_value)
        self._cache.set(key_name, key_value)

    def delete_key(self, key_name: SecureStorageKey) -> None:
        if key_name in [SecureStorageKey.AESGCMCipherKey, SecureStorageKey.AESGCMCipherKeyBackup]:
            raise IllegalAESGCMCipherAccessError

        self._delete_password(key_name)
        self._cache.delete(key_name)

    def clear(self) -> None:
        self._cache.destroy()

    def destroy(self) -> None:
        if self._cache:
            self._cache.destroy()

        for key in SECURE_STORAGE_KEY_LIST:
            try:
                self._delete_password(key)
            except keyring.errors.PasswordDeleteError:
                print(f"`{key}` could not found in keyring to delete. Skipping...")
                pass

class SecureStorageCache:
    class CachedData(TypedDict):
        data: any
        created_at: float

    _instance = None
    _store: dict[str, CachedData]

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._store = {}

        return cls._instance

    def __del__(self):
        self.destroy()

    def _is_expired(self, timestamp: float) -> bool:
        return time.time() - timestamp > CACHE_TTL

    def get(self, key: str) -> any:
        if key not in self._store:
            return None

        store_data: SecureStorageCache.CachedData = self._store[key]
        if self._is_expired(store_data["created_at"]):
            self.delete(key)

        return store_data.value

    def set(self, key: str, value: any):
        self._store[key] = {
            "data": value,
            "created_at": time.time()
        }

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
