from enum import Enum
from typing import Optional

from pydantic import BaseModel

from .secure_storage import SecureStorage, SecureStorageKey

"""
Exceptions
"""
class InvalidAccountColumnError(Exception):
    """Invalid account column."""
    pass

"""
Enums, Types
"""
class AccountColumn(str, Enum):
    EMAIL_ADDRESS = "email_address"
    PASSWORD = "password"
    FULLNAME = "fullname"

    @classmethod
    def keys(cls) -> list[str]:
        return [key.value for key in cls]

    def __str__(self) -> str:
        return self.value

class Account(BaseModel):
    email_address: str
    password: Optional[str] = None
    fullname: Optional[str] = None

"""
Constants
"""
ACCOUNT_COLUMN_LIST = AccountColumn.keys()

class AccountManager:
    _instance = None
    _secure_storage: SecureStorage = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._secure_storage = SecureStorage()
            cls._instance._create()

        return cls._instance

    def __del__(self):
        self.clear()

    def _check_columns(self, columns: list[str | AccountColumn]) -> None:
        for column in columns:
            if str(column) not in ACCOUNT_COLUMN_LIST:
                raise InvalidAccountColumnError

    def has_any(self) -> bool:
        accounts = self._secure_storage.get_key_value(
            SecureStorageKey.ACCOUNTS,
            decrypt=False
        )
        return bool(accounts)

    def _create(self) -> None:
        if self.has_any():
            return

        self._secure_storage.add_key(SecureStorageKey.ACCOUNTS, [])

    def get(self,
        emails: list[str] | None = None,
        columns: list[AccountColumn] | None = None
    ) -> list[Account] | None:
        if columns:
            self._check_columns(columns)
        else:
            columns = ACCOUNT_COLUMN_LIST

        accounts = self._secure_storage.get_key_value(SecureStorageKey.ACCOUNTS)
        if not accounts:
            return []

        columns = [column.value if isinstance(column, AccountColumn) else column for column in columns]

        filtered_accounts = []
        for account in accounts:
            if emails and account["email_address"] not in emails:
                continue

            filtered_accounts.append(
                Account.model_validate({column: account[column] for column in columns})
            )

        return filtered_accounts

    def add(self, account: Account) -> None:
        accounts = self.get()
        if not accounts:
            accounts = []

        accounts = [account.model_dump() for account in accounts]
        accounts.append(account.model_dump())
        self._secure_storage.add_key(
            SecureStorageKey.ACCOUNTS,
            accounts
        )

    def edit(self, account: Account) -> None:
        accounts = self.get()
        if not accounts:
            return

        i = 0
        while i < len(accounts):
            if accounts[i].email_address == account.email_address:
                accounts[i] = account
                break
            i += 1

        accounts = [account.model_dump() for account in accounts]
        accounts.append(account.model_dump())
        self._secure_storage.add_key(
            SecureStorageKey.ACCOUNTS,
            accounts
        )

    def remove(self, email: str) -> None:
        accounts = self.get()
        if not accounts:
            return

        accounts = [account.model_dump() for account in accounts if account.email_address != email]
        self._secure_storage.add_key(
            SecureStorageKey.ACCOUNTS,
            accounts
        )

    def remove_all(self) -> None:
        self._secure_storage.delete_key(SecureStorageKey.ACCOUNTS)
        self._create() # Create empty list for later use

    def destroy(self) -> None:
        self._secure_storage.destroy()

    def clear(self) -> None:
        self._secure_storage.clear()

__all__ = [
    "AccountManager",
    "Account",
    "AccountColumn",
    "InvalidAccountColumnError"
]
