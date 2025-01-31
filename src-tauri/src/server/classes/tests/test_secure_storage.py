import unittest
import json
from typing import cast

from classes.secure_storage import SECURE_STORAGE_KEY_LIST, SecureStorage, SecureStorageKey, RSACipher, SecureStorageKeyValueType

class TestSecureStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO: Check also cache in every method.
        print("Setting up test `TestSecureStorage`...")
        cls.addClassCleanup(cls.cleanup)
        cls._secure_storage = SecureStorage()

        cls._secure_storage.add_key(
            SecureStorageKey.CompleteBackupBeforeTesting,
            [
                cls._secure_storage.get_key_value(
                    cast(SecureStorageKey, key_name)
                )
                for key_name in SECURE_STORAGE_KEY_LIST
            ],
            SecureStorageKeyValueType.TestingKey
        )

    def test_add_key(self):
        pass

    def test_get_key_value(self):
        pass

    def test_update_key(self):
        pass

    def test_delete_key(self):
        pass

    def test_clear(self):
        pass

    def test_destroy(self):
        pass

    def test_aesgcm_encryption(self):
        pass

    def test_aesgcm_decryption(self):
        pass

    def test_aesgcm_rotation(self):
        pass

    def test_rsa_encryption(self):
        pass

    def test_rsa_decryption(self):
        pass

    def test_rsa_rotation(self):
        pass

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestSecureStorage`...")
