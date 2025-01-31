import unittest
import json
from typing import cast

from classes.secure_storage import SECURE_STORAGE_KEY_LIST, SecureStorage, SecureStorageKey, RSACipher, SecureStorageKeyValueType
from consts import APP_NAME

import keyring

COMPLETE_BACKUP_BEFORE_TESTING = "complete_backup_before_testing"

class TestSecureStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO: Check also cache in every method.
        print("Setting up test `TestSecureStorage`...")
        cls.addClassCleanup(cls.cleanup)
        cls._secure_storage = SecureStorage()

        keyring.set_password(
            APP_NAME,
            COMPLETE_BACKUP_BEFORE_TESTING,
            [
                {
                    "key_name": key_name,
                    "key_value":
                        cls._secure_storage.get_key_value(
                            cast(SecureStorageKey, key_name)
                        )
                } for key_name in SECURE_STORAGE_KEY_LIST
            ]
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
        complete_backup_before_testing = keyring.get_password(
            APP_NAME,
            COMPLETE_BACKUP_BEFORE_TESTING
        )
        if not complete_backup_before_testing:
            raise Exception("Error: Backup could not found.")

        for key_name in SECURE_STORAGE_KEY_LIST + [COMPLETE_BACKUP_BEFORE_TESTING]:
            keyring.delete_password(APP_NAME, key_name)

        for data in complete_backup_before_testing:
            data = json.loads(data)
            keyring.set_password(APP_NAME, data["key_name"], data["key_value"])
