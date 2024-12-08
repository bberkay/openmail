from __future__ import annotations
import base64
import os
import json
import time
from enum import Enum
from typing import TypedDict
from dataclasses import dataclass

import keyring
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from utils import safe_json_loads
from consts import APP_NAME

"""
Exceptions
"""
class CipherNotInitializedError(Exception):
    """Cipher is not initialized."""
    pass

class InvalidSecureStorageKeyError(Exception):
    """Invalid secure storage key."""
    pass

class InvalidAccountColumnError(Exception):
    """Invalid account column."""
    pass

"""
Enums, Types
"""
class SecureStorageKey(Enum):
    CIPHER_KEY = "CIPHER_KEY"
    ACCOUNTS = "ACCOUNTS"

    @classmethod
    def keys(cls) -> list[str]:
        return [key.value for key in cls]

    def __str__(self) -> str:
        return self.value

class AccountColumn(Enum):
    EMAIL = "EMAIL"
    PASSWORD = "PASSWORD"
    FULLNAME = "FULLNAME"

    @classmethod
    def keys(cls) -> list[str]:
        return [key.value for key in cls]

    def __str__(self) -> str:
        return self.value

class Account(TypedDict):
    email: str
    password: str
    fullname: str | None

"""
Constants
"""
SECURE_STORAGE_KEY_LIST = SecureStorageKey.keys()
ACCOUNT_COLUMN_LIST = AccountColumn.keys()
CACHE_TTL = 1800

class SecureStorage:
    _instance = None
    _cache: SecureStorageCache = None
    _encryptor: AESGCMCipher = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._cache = SecureStorageCache()
            cls._instance._encryptor = AESGCMCipher(cls._instance._load_key())
            cls._instance._create_accounts()

        return cls._instance

    def __del__(self):
        self.clear()

    def _load_key(self):
        key_name = self._check_and_format_key(SecureStorageKey.CIPHER_KEY)
        key = keyring.get_password(APP_NAME, key_name)
        if not key:
            key = os.urandom(32).hex()
            keyring.set_password(APP_NAME, key_name, key)

        return bytes.fromhex(key)

    def _create_accounts(self) -> None:
        if self.has_any_accounts():
            return

        self._add_key(SecureStorageKey.ACCOUNTS, [])

    def _check_and_format_key(self, key: str | SecureStorageKey) -> str:
        key_name = str(key).upper()
        if key_name not in SECURE_STORAGE_KEY_LIST:
            raise InvalidSecureStorageKeyError
        return key_name

    def _get_key_value(self, key_name: SecureStorageKey, associated_data: bytes = None, decrypt: bool = True) -> any:
        key_name = self._check_and_format_key(key_name)

        key_value = self._cache.get(key_name)
        if not key_value:
            key_value = keyring.get_password(APP_NAME, key_name)
            if not key_value:
                return None
            self._cache.set(key_name, key_value)

        if decrypt:
            if self._encryptor:
                key_value = self._encryptor.decrypt(key_value, associated_data)
                key_value = safe_json_loads(key_value)
            else:
                raise CipherNotInitializedError

        return key_value

    def _add_key(self, key_name: SecureStorageKey, key_value: any, associated_data: bytes = None):
        key_name = self._check_and_format_key(key_name)

        key_value = json.dumps(key_value)
        if not self._encryptor:
            raise CipherNotInitializedError

        key_value = self._encryptor.encrypt(key_value, associated_data)
        keyring.set_password(APP_NAME, key_name, key_value)
        self._cache.set(key_name, key_value)

    def _check_and_format_columns(self, columns: list[str | AccountColumn]) -> list[str]:
        upper_columns = []
        for column in columns:
            column_name = str(column).upper()
            if column_name not in ACCOUNT_COLUMN_LIST:
                raise InvalidAccountColumnError
            upper_columns.append(column_name)

        return upper_columns

    def has_any_accounts(self) -> bool:
        accounts = self._get_key_value(SecureStorageKey.ACCOUNTS, decrypt=False)
        return bool(accounts)

    def get_accounts(self, emails: list[str] | None = None, columns: list[AccountColumn] | None = None) -> list[Account] | None:
        if columns:
            columns = self._check_and_format_columns(columns)
        else:
            columns = ACCOUNT_COLUMN_LIST

        accounts: list[Account] = self._get_key_value(SecureStorageKey.ACCOUNTS)

        filtered_accounts = []
        for account in accounts:
            if emails and account["email"] not in emails:
                continue
            filtered_accounts.append({column: account[column] for column in columns})

        return filtered_accounts

    def insert_account(self, account: Account):
        accounts = self.get_accounts()
        if not accounts:
            accounts = []

        accounts.append(account)
        self._add_key(SecureStorageKey.ACCOUNTS, accounts)

    def delete_account(self, email: str):
        accounts = self.get_accounts()
        if not accounts:
            return

        self._add_key(
            SecureStorageKey.ACCOUNTS,
            filter(lambda account: account["email"] != email, accounts)
        )

    def delete_accounts(self):
        keyring.delete_password(APP_NAME, SecureStorageKey.ACCOUNTS)
        self._cache.delete(SecureStorageKey.ACCOUNTS)
        self._create_accounts() # Create empty list

    def clear(self):
        self._cache.destroy()

    def destroy(self):
        if self._cache:
            self._cache.destroy()

        try:
            for key in SECURE_STORAGE_KEY_LIST:
                keyring.delete_password(APP_NAME, key)
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

__all__ = ["SecureStorage", "Account", "AccountColumn"]
