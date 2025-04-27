import unittest
import json

from modules.openmail import Openmail
from modules.openmail.utils import contains_non_ascii

class TestConnectOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestFolderOperations`...")
        cls.addClassCleanup(cls.cleanup)

        cls._openmail = Openmail()
        with open("./credentials.json") as credentials:
            cls._credentials = json.load(credentials)
        if len(cls._credentials) < 3:
            raise ValueError("At least 3 credentials are required.")

    def test_login(self):
        print("test_login...")
        failed_accounts = []
        for credential in self.__class__._credentials:
            status, message = self.__class__._openmail.connect(
                credential["email"],
                credential["password"]
            )

            if status:
                print(f"Successfully logged in {credential["email"]}")
            else:
                failed_accounts.append({"email": credential["email"], "status": status, "message": message})

            self.__class__._openmail.disconnect()

        if len(failed_accounts) > 0:
            self.fail(f"There were accounts that could not be logged in: {failed_accounts}")

    def test_login_with_nonascii_email(self):
        print("test_login_with_nonascii_email...")
        failed_accounts = []
        for credential in self.__class__._credentials:
            if not contains_non_ascii(credential["email"]):
                print(f"{credential["email"]} does not include nonascii character. Skipping...")
                continue

            status, message = self.__class__._openmail.connect(
                credential["email"],
                credential["password"]
            )

            if status:
                print(f"Successfully logged in {credential["email"]}")
            else:
                failed_accounts.append({"email": credential["email"], "status": status, "message": message})

            self.__class__._openmail.disconnect()

        if len(failed_accounts) > 0:
            self.fail(f"There were accounts that could not be logged in: {failed_accounts}")

    def test_login_with_nonascii_password(self):
        print("test_login_with_nonascii_password...")
        failed_accounts = []
        for credential in self.__class__._credentials:
            if not contains_non_ascii(credential["password"]):
                print(f"{credential["email"]} does not include nonascii character. Skipping...")
                continue

            status, message = self.__class__._openmail.connect(
                credential["email"],
                credential["password"]
            )

            if status:
                print(f"Successfully logged in {credential["email"]}")
            else:
                failed_accounts.append({"email": credential["email"], "status": status, "message": message})

            self.__class__._openmail.disconnect()

        if len(failed_accounts) > 0:
            self.fail(f"There were accounts that could not be logged in: {failed_accounts}")

    def test_logout(self):
        print("test_logout...")
        logged_in_failed_accounts = []
        logged_out_failed_accounts = []
        for credential in self.__class__._credentials:
            status, message = self.__class__._openmail.connect(
                credential["email"],
                credential["password"]
            )

            if status:
                print(f"Successfully logged in {credential["email"]}")
            else:
                logged_in_failed_accounts.append({"email": credential["email"], "status": status, "message": message})

            status, message = self.__class__._openmail.disconnect()
            if status:
                print(f"Successfully logged out from {credential["email"]}")
            else:
                logged_out_failed_accounts.append({"email": credential["email"], "status": status, "message": message})

        if len(logged_in_failed_accounts) > 0:
            self.fail(f"There were accounts that could not be logged in: {logged_in_failed_accounts}")

        if len(logged_out_failed_accounts) > 0:
            self.fail(f"There were accounts that could not be logged out: {logged_out_failed_accounts}")

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestConnectOperations`...")
        cls._openmail.disconnect()
