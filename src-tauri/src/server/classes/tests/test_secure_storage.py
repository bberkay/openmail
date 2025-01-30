import unittest
import json

from classes.secure_storage import SecureStorage, SecureStorageKey, RSACipher

class TestSecureStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestSecureStorage`...")
        cls.addClassCleanup(cls.cleanup)

        cls._secure_storage = SecureStorage()
        with open("./credentials.json") as credentials:
            credentials = json.load(credentials)

    def test_add_key(self):
        pass

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestConnectOperations`...")
        cls._openmail.disconnect()
