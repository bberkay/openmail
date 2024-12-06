import json
from typing import List

import keyring
from cryptography.fernet import Fernet

from consts import APP_NAME


class CipherKeyNotFoundError(Exception):
    """Cipher key is not found in the keyring."""
    pass


class SecureStorage:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._cipher = None
        self._create_cipher_key()
        self._create_accounts()

    def _get_cipher_key(self) -> str | None:
        return keyring.get_password(APP_NAME, "cipher_key")

    def _create_cipher_key(self) -> None:
        if self._get_cipher_key() is None:
            keyring.set_password(
                APP_NAME,
                "cipher_key",
                Fernet.generate_key().decode()
            )
        self._initialize_cipher()

    def _initialize_cipher(self) -> None:
        """Initialize the Fernet instance with the stored cipher key."""
        cipher_key = self._get_cipher_key()
        if cipher_key is not None:
            self._cipher = Fernet(cipher_key)
        else:
            raise CipherKeyNotFoundError("Cipher key is missing; cannot initialize encryption.")

    def _create_accounts(self) -> None:
        if self._get_key("accounts") is None:
            self._add_key("accounts", "[]")

    def _get_key(self, key: str) -> str | None:
        if not self._cipher:
            self._initialize_cipher()

        key_value = keyring.get_password(APP_NAME, key)
        if key_value:
            return self._cipher.decrypt(key_value.encode()).decode()
        return None

    def _add_key(self, key_name: str, key_value: str) -> None:
        if not self._cipher:
            self._initialize_cipher()

        encrypted_value = self._cipher.encrypt(key_value.encode()).decode()
        keyring.set_password(APP_NAME, key_name, encrypted_value)

    def insert_account(self, email: str, password: str, fullname: str | None = None) -> None:
        """Insert a new account, securely encrypting the password."""
        accounts = self.get_accounts()
        if accounts is None:
            accounts = []

        accounts.append({
            "email": email,
            "password": self._cipher.encrypt(password.encode()).decode(),
            "fullname": fullname
        })
        self._add_key("accounts", json.dumps(accounts))

    def get_accounts(self, emails: List[str] | None = None, columns: List[str] | None = None) -> list[dict] | None:
        """Retrieve accounts and decrypt passwords."""
        if not columns:
            columns = ["fullname", "email", "password"]

        accounts = self._get_key("accounts")
        accounts = json.loads(accounts) if accounts else []

        for account in accounts:
            account["password"] = self._cipher.decrypt(account["password"].encode()).decode()

        if emails:
            accounts = [account for account in accounts if account["email"] in emails]
        if columns:
            accounts = [{column: account[column] for column in columns} for account in accounts]
        return accounts

    def delete_account(self, email: str) -> None:
        """Delete a specific account by email."""
        accounts = self.get_accounts()
        if accounts is None:
            return None
        accounts = [account for account in accounts if account["email"] != email]
        self._add_key("accounts", json.dumps(accounts))

    def delete_accounts(self) -> None:
        """Delete all accounts."""
        self._add_key("accounts", "[]")
