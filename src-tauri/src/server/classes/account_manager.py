import json
from typing import Optional

from pydantic import BaseModel

from .secure_storage import SecureStorage, SecureStorageKey, SecureStorageKeyValue, SecureStorageKeyValueType

"""
Errors
"""
class AccountAlreadyExists(Exception):
    def __init__(self, msg: str = "Account already exists.", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

class AccountDoesNotExists(Exception):
    def __init__(self, msg: str = "Account does not exists.", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)

"""
Enums, Types
"""
class Account(BaseModel):
    email_address: str
    fullname: Optional[str] = None

class AccountWithPassword(Account):
    encrypted_password: str = ""

class AccountManager:
    _instance = None
    _secure_storage: SecureStorage

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._secure_storage = SecureStorage()

        return cls._instance

    def is_exists(self, email: str) -> bool:
        return bool(self.get(email_address=email, include_password=False))

    def get(self,
        email_address: str,
        include_password: bool = True
    ) -> Account | AccountWithPassword | None:
        accounts = self._secure_storage.get_key_value(SecureStorageKey.Accounts)
        if not accounts:
            return None

        accounts = json.loads(accounts["value"].replace("'", "\""))
        for account in accounts:
            if account["email_address"] != email_address:
                continue
            if include_password:
                return AccountWithPassword.model_validate(account)
            else:
                return Account.model_validate(account)

        return None

    def get_some(self,
        email_addresses: list[str],
        include_passwords: bool = True
    ) -> list[Account] | list[AccountWithPassword]:
        accounts = self._secure_storage.get_key_value(SecureStorageKey.Accounts)
        if not accounts:
            return []

        accounts = json.loads(accounts["value"].replace("'", "\""))

        filtered_accounts = []
        for account in accounts:
            if email_addresses and account["email_address"] not in email_addresses:
                continue

            if include_passwords:
                filtered_accounts.append(AccountWithPassword.model_validate(account))
            else:
                filtered_accounts.append(Account.model_validate(account))
        return filtered_accounts

    def get_all(self,
        include_passwords: bool = True
    ) -> list[Account] | list[AccountWithPassword]:
        accounts = self._secure_storage.get_key_value(SecureStorageKey.Accounts)
        if not accounts:
            return []

        accounts = json.loads(accounts["value"].replace("'", "\""))

        return self.get_some(
            [account["email_address"] for account in accounts],
            include_passwords
        )

    def add(self, account: AccountWithPassword) -> None:
        if self.is_exists(account.email_address):
            raise AccountAlreadyExists

        accounts = self.get_all()
        if not accounts:
            accounts = []

        accounts = [account.model_dump() for account in accounts]
        accounts.append(account.model_dump())
        self._secure_storage.update_key(
            SecureStorageKey.Accounts,
            accounts,
            SecureStorageKeyValueType.RSAEncrypted
        )

    def edit(self, account: Account | AccountWithPassword) -> None:
        """Edit account by email address"""
        if not self.is_exists(account.email_address):
            raise AccountDoesNotExists

        include_passwords = isinstance(account, AccountWithPassword) and bool(account.encrypted_password)
        accounts = self.get_all(include_passwords=include_passwords)
        if not accounts:
            return

        i = 0
        while i < len(accounts):
            if accounts[i].email_address == account.email_address:
                accounts[i] = account
                break
            i += 1

        accounts = [account.model_dump() for account in accounts]
        self._secure_storage.update_key(
            SecureStorageKey.Accounts,
            accounts,
            SecureStorageKeyValueType.RSAEncrypted
        )

    def remove(self, email_address: str) -> None:
        if not self.is_exists(email_address):
            return None

        accounts = self.get_all()
        if not accounts:
            return

        accounts = [account.model_dump() for account in accounts if account.email_address != email_address]
        self._secure_storage.update_key(
            SecureStorageKey.Accounts,
            accounts,
            SecureStorageKeyValueType.RSAEncrypted
        )

    def remove_all(self) -> None:
        self._secure_storage.delete_key(SecureStorageKey.Accounts)

__all__ = [
    "AccountManager",
    "Account",
    "AccountWithPassword"
]
