import json
from typing import Optional

from pydantic import BaseModel

from .secure_storage import SecureStorage, SecureStorageKey, SecureStorageKeyValue, SecureStorageKeyValueType

"""
Enums, Types
"""
class Account(BaseModel):
    email_address: str
    fullname: Optional[str] = None

class AccountWithPassword(Account):
    encrypted_password: str = None

class AccountManager:
    _instance = None
    _secure_storage: SecureStorage = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._secure_storage = SecureStorage()

        return cls._instance

    def __del__(self):
        self.clear()

    def is_exists(self, email: str) -> bool:
        return bool(self.get(emails=email, include_encrypted_passwords=False))

    def get(self,
        emails: str | list[str] | None = None,
        include_encrypted_passwords: bool = True
    ) -> list[Account] | None:
        accounts = self._secure_storage.get_key_value(SecureStorageKey.Accounts)
        if not accounts:
            return []

        accounts = json.loads(accounts["value"].replace("'", "\""))
        if isinstance(emails, str):
            emails = [emails]

        filtered_accounts = []
        for account in accounts:
            if emails and account["email_address"] not in emails:
                continue

            if include_encrypted_passwords:
                filtered_accounts.append(AccountWithPassword.model_validate(account))
            else:
                filtered_accounts.append(Account.model_validate(account))
        return filtered_accounts

    def add(self, account: AccountWithPassword) -> None:
        accounts = self.get()
        if not accounts:
            accounts = []

        accounts = [account.model_dump() for account in accounts]
        accounts.append(account.model_dump())
        self._secure_storage.add_key(
            SecureStorageKey.Accounts,
            SecureStorageKeyValue(
                value=accounts,
                type=SecureStorageKeyValueType.RSAEncryptedKey
            )
        )

    def edit(self, account: Account | AccountWithPassword) -> None:
        accounts = self.get(include_encrypted_passwords=bool(account.encrypted_password))
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
            SecureStorageKey.Accounts,
            SecureStorageKeyValue(
                value=accounts,
                type=SecureStorageKeyValueType.RSAEncryptedKey
            )
        )

    def remove(self, email: str) -> None:
        accounts = self.get()
        if not accounts:
            return

        accounts = [account.model_dump() for account in accounts if account.email_address != email]
        self._secure_storage.add_key(
            SecureStorageKey.Accounts,
            SecureStorageKeyValue(
                value=accounts,
                type=SecureStorageKeyValueType.RSAEncryptedKey
            )
        )

    def remove_all(self) -> None:
        self._secure_storage.delete_key(SecureStorageKey.Accounts)

    def destroy(self) -> None:
        self._secure_storage.destroy()

    def clear(self) -> None:
        self._secure_storage.clear()

__all__ = [
    "AccountManager",
    "Account",
    "AccountWithPassword"
]
