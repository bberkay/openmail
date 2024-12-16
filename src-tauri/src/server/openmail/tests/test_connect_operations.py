import unittest

from openmail import OpenMail

class TestConnectOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestFolderOperations`...")
        cls._openmail = OpenMail()

    def test_login(self):
        print("test_login...")
        status, message = self.__class__._openmail.connect(

        )
        if status:
            print(message)
        else:
            self.fail(f"Failed to login with status: {status} and message: {message}")

    def test_login_with_nonascii_email(self):
        print("test_login_with_utf8_email...")
        status, message = self.__class__._openmail.connect(
            "test-ü"
        )
        if status:
            print(message)
        else:
            self.fail(f"Failed to login with status: {status} and message: {message}")

    def test_login_with_nonascii_password(self):
        print("test_login_with_utf8_password...")
        status, message = self.__class__._openmail.connect(
            "test-username",
            "test-password-ü"
        )
        if status:
            print(message)
        else:
            self.fail(f"Failed to login with status: {status} and message: {message}")

    def test_logout(self):
        print("test_logout...")
        status, message = self.__class__._openmail.disconnect()
        if status:
            print(message)
        else:
            self.fail(f"Failed to logout with status: {status} and message: {message}")
