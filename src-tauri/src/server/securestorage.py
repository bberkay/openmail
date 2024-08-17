import json
from typing import List

import keyring
from cryptography.fernet import Fernet

from consts import APP_NAME

class SecureStorage:
    def __init__(self):
        pass

    def init(self) -> None:
        self.__create_cipher_key()
        self.__create_accounts()

    def __get_cipher_key(self) -> None:
        return keyring.get_password(APP_NAME, "cipher_key")

    def __create_cipher_key(self) -> None:
        if self.__get_cipher_key() is None:
            keyring.set_password(
                APP_NAME,
                "cipher_key",
                Fernet.generate_key().decode()
            )

    def __create_accounts(self) -> None:
        if self.__get_key("accounts") is None:
            self.__add_key("accounts", "[]")

    def __get_key(self, key: str) -> str | None:
        cipher_key = self.__get_cipher_key()
        if cipher_key is not None:
            cipher = Fernet(cipher_key)
            key = keyring.get_password(APP_NAME, key)
            if key is not None:
                return cipher.decrypt(
                    key.encode()
                ).decode()
            return None
        else:
            raise Exception("Cipher key not found for decryption")

    def __add_key(self, key_name: str, key_value: str) -> None:
        cipher_key = self.__get_cipher_key()
        if cipher_key is not None:
            cipher = Fernet(cipher_key)
            keyring.set_password(
                APP_NAME,
                key_name,
                cipher.encrypt(
                    key_value.encode()
                ).decode()
            )
        else:
            raise Exception("Cipher key not found for encryption")

    def insert_account(self, email: str, password: str, fullname: str | None = None) -> None:
        accounts = self.get_accounts()
        if accounts is None:
            accounts = []
        accounts.append({
            "email": email,
            "password": password,
            "fullname": fullname
        })
        self.__add_key("accounts", json.dumps(accounts))

    def get_accounts(self, emails: List[str] | None = None, columns: List[str] = ["fullname", "email", "password"]) -> list[dict] | None:
        accounts = self.__get_key("accounts")
        accounts = json.loads(accounts) if accounts else []
        if emails:
            accounts = [account for account in accounts if account["email"] in emails]
        if columns:
            accounts = [{column: account[column] for column in columns} for account in accounts]
        return accounts

    def delete_accounts(self) -> None:
        self.__add_key("accounts", "[]")

    def delete_account(self, email: str) -> None:
        accounts = self.get_accounts()
        if accounts is None:
            return None
        accounts = [account for account in accounts if account["email"] != email]
        self.__add_key("accounts", json.dumps(accounts))
