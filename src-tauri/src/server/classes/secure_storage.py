import json
from typing import List, TypedDict
from enum import Enum

import keyring
from cryptography.fernet import Fernet

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
    CIPHER_KEY = "cipher_key"
    ACCOUNTS = "accounts"

    @classmethod
    def keys(cls) -> list[str]:
        return [key.name for key in cls]

class AccountColumn(Enum):
    EMAIL = "email"
    PASSWORD = "password"
    FULLNAME = "fullname"

    @classmethod
    def keys(cls) -> list[str]:
        return [key.name for key in cls]

class Account(TypedDict):
    email: str
    password: str
    fullname: str | None

"""
Constants
"""
SECURE_STORAGE_KEY_LIST = SecureStorageKey.list()
ACCOUNT_COLUMN_LIST = AccountColumn.list()

class SecureStorage:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)

            # Initialize the cipher
            cls._instance._cache = {}
            cls._instance._cipher = None
            cls._instance._create_cipher()
            cls._instance._create_accounts()

        return cls._instance

    def __del__(self):
        self._clear_cache()

    def _clear_cache(self):
        self._cache = {}

    def _create_cipher(self):
        if self._cipher:
            return

        if self._get_key(SecureStorageKey.CIPHER_KEY):
            cipher_key = self._get_key(SecureStorageKey.CIPHER_KEY)
        else:
            cipher_key = Fernet.generate_key().decode()
            keyring.set_password(APP_NAME, SecureStorageKey.CIPHER_KEY, cipher_key)

        self._cipher = Fernet(cipher_key)

    def _create_accounts(self) -> None:
        if self._get_key(SecureStorageKey.ACCOUNTS):
            return

        self._add_key("accounts", [])

    def _check_key(self, key: str) -> None:
        if key not in SECURE_STORAGE_KEY_LIST:
            raise InvalidSecureStorageKeyError

    def _get_key(self, key: SecureStorageKey) -> str | None:
        self._check_key(key)

        if not self._cipher:
            raise CipherNotInitializedError

        if key in self._cache:
            return self._cache[key]

        key = keyring.get_password(APP_NAME, key)
        if not key:
            return None

        decrypted_key = self._cipher.decrypt(key.encode()).decode()

        self._cache[key] = decrypted_key
        return decrypted_key

    def _add_key(self, key_name: SecureStorageKey, key_value: any) -> None:
        self._check_key(key_name)

        if not self._cipher:
            raise CipherNotInitializedError

        decrypted_key = self._cipher.decrypt(json.dumps(key_value).encode()).decode()
        keyring.set_password(APP_NAME, key_name, decrypted_key)
        self._cache[key_name] = decrypted_key

    def _check_columns(self, columns: List[str]) -> None:
        for column in columns:
            if column not in ACCOUNT_COLUMN_LIST:
                raise InvalidAccountColumnError

    def get_accounts(self, emails: List[str] | None = None, columns: List[AccountColumn] | None = None) -> List[Account] | None:
        if columns:
            self._check_columns(columns)
        else:
            columns = ACCOUNT_COLUMN_LIST

        accounts = self._get_key(SecureStorageKey.ACCOUNTS)
        accounts: List[Account] = json.loads(accounts) if accounts else []

        filtered_accounts = []
        for account in accounts:
            if emails and account["email"] not in emails:
                continue
            filtered_accounts.append({column: account[column] for column in columns})

        return filtered_accounts

    def insert_account(self, account: Account) -> None:
        accounts = self.get_accounts()
        if not accounts:
            accounts = []

        accounts.append(account)
        self._add_key(SecureStorageKey.ACCOUNTS, accounts)

    def delete_account(self, email: str) -> None:
        accounts = self.get_accounts()
        if not accounts:
            return None

        self._add_key(
            SecureStorageKey.ACCOUNTS,
            filter(lambda account: account["email"] != email, accounts)
        )

    def delete_accounts(self) -> None:
        self._add_key(SecureStorageKey.ACCOUNTS, [])
