import time
import unittest
import json
from typing import cast

from classes.tests.utils.name_generator import NameGenerator
from classes.secure_storage import *
from classes.secure_storage import SECURE_STORAGE_ILLEGAL_ACCESS_KEY_LIST
from classes.secure_storage import SECURE_STORAGE_KEY_LIST

class TestSecureStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestSecureStorage`...")
        cls.addClassCleanup(cls.cleanup)
        cls._secure_storage = SecureStorage()
        cls._test_backup_id = cls._secure_storage._create_backup()

    def check_cache(self):
        print("Checking Cache...")
        key_values = [
            self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey, decrypt=False),
            self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey, use_cache=False, decrypt=False),
            self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey),
        ]
        self.assertEqual(
            len(set([key_value["value"] for key_value in key_values if key_value])),
            1
        )

    def test_create_backup(self):
        print("test_create_backup...")
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            NameGenerator.email_address()[0],
            SecureStorageKeyValueType.AESGCMEncrypted
        )

        time.sleep(1)

        current_key_values = []
        for key in SECURE_STORAGE_KEY_LIST:
            if key == SecureStorageKey.Backups:
                continue

            key_value = self.__class__._secure_storage._get_password(
                cast(SecureStorageKey, key)
            )
            current_key_values.append({
                "key_name": key,
                "key_value": key_value
            })

        new_backup_id = self.__class__._secure_storage._create_backup()
        found_key_value = self.__class__._secure_storage._get_password(SecureStorageKey.Backups)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.Backups}'s value could not found.")

        self.assertCountEqual(
            current_key_values,
            [backup for backup in found_key_value["value"] if backup["backup_id"] == new_backup_id][0]["backup_data"]
        )

        self.__class__._secure_storage._delete_backup(new_backup_id)

        # Check Cache
        self.assertIsNotNone(self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey))

    def test_load_backup(self):
        print("test_load_backup...")
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            NameGenerator.email_address()[0],
            SecureStorageKeyValueType.AESGCMEncrypted
        )

        time.sleep(1)

        pre_load_backup_key_values = []
        for key in SECURE_STORAGE_KEY_LIST:
            if key == SecureStorageKey.Backups:
                continue
            key_value = self.__class__._secure_storage._get_password(
                cast(SecureStorageKey, key)
            )
            pre_load_backup_key_values.append({
                "key_name": key,
                "key_value": key_value
            })

        new_backup_id = self.__class__._secure_storage._create_backup()
        found_key_value = self.__class__._secure_storage._get_password(SecureStorageKey.Backups)
        self.assertIsNotNone(found_key_value)

        self.__class__._secure_storage.delete_key(SecureStorageKey.TestKey)
        found_key_value = self.__class__._secure_storage._get_password(SecureStorageKey.TestKey)
        self.assertIsNone(found_key_value)

        self.__class__._secure_storage._load_backup(new_backup_id)

        post_load_backup_key_values = []
        for key in SECURE_STORAGE_KEY_LIST:
            if key == SecureStorageKey.Backups:
                continue
            key_value = self.__class__._secure_storage._get_password(
                cast(SecureStorageKey, key)
            )
            post_load_backup_key_values.append({
                "key_name": key,
                "key_value": key_value
            })

        self.assertCountEqual(
            pre_load_backup_key_values,
            post_load_backup_key_values
        )

        self.__class__._secure_storage._delete_backup(new_backup_id)

        # Check Cache
        self.assertIsNone(self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey))

    def test_delete_backup(self):
        print("test_delete_backup...")
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            NameGenerator.email_address()[0],
            SecureStorageKeyValueType.AESGCMEncrypted
        )

        time.sleep(1)

        new_backup_id = self.__class__._secure_storage._create_backup()
        found_key_value = self.__class__._secure_storage._get_password(SecureStorageKey.Backups)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.Backups}'s value could not found after creating new backup.")

        self.assertIn(
            new_backup_id,
            [backup["backup_id"] for backup in found_key_value["value"]]
        )

        self.__class__._secure_storage._delete_backup(new_backup_id)
        found_key_value = self.__class__._secure_storage._get_password(SecureStorageKey.Backups)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.Backups}'s value could not found after deleting backup.")

        self.assertNotIn(
            new_backup_id,
            [backup["backup_id"] for backup in found_key_value["value"]]
        )

        # Check Cache
        self.assertIsNotNone(self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey))

    def test_get_key_value(self):
        print("test_get_key_value...")
        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        found_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey, use_cache=False)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(found_key_value["value"], test_key_value["value"])
        self.assertEqual(found_key_value["type"], test_key_value["type"])

        self.check_cache()

    def test_get_invalid_key_value(self):
        print("test_get_invalid_key_value...")
        with self.assertRaises(InvalidSecureStorageKeyError):
            self.__class__._secure_storage.get_key_value(
                "invalidkey",
            )

    def test_get_illegal_key_value(self):
        print("test_get_illegal_key_value...")
        with self.assertRaises(IllegalSecureStorageKeyError):
            self.__class__._secure_storage.get_key_value(
                SECURE_STORAGE_ILLEGAL_ACCESS_KEY_LIST[0]
            )

    def test_add_key(self):
        print("test_add_key...")
        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        found_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(found_key_value["value"], test_key_value["value"])
        self.assertEqual(found_key_value["type"], test_key_value["type"])

        self.check_cache()

    def test_add_invalid_key(self):
        print("test_add_invalid_key...")
        with self.assertRaises(InvalidSecureStorageKeyError):
            self.__class__._secure_storage.add_key(
                "invalidkey",
                NameGenerator.email_address()[0],
                SecureStorageKeyValueType.AESGCMEncrypted,
            )

    def test_add_illegal_key(self):
        print("test_add_illegal_key...")
        with self.assertRaises(IllegalSecureStorageKeyError):
            self.__class__._secure_storage.add_key(
                SECURE_STORAGE_ILLEGAL_ACCESS_KEY_LIST[0],
                NameGenerator.email_address()[0],
                SecureStorageKeyValueType.AESGCMEncrypted
            )

    def test_add_invalid_key_value_type(self):
        print("test_add_invalid_key_value_type...")
        with self.assertRaises(InvalidSecureStorageKeyValueTypeError):
            self.__class__._secure_storage.add_key(
                SecureStorageKey.TestKey,
                NameGenerator.email_address()[0],
                "invalidkeyvaluetype",
            )

    def test_override_by_add(self):
        print("test_override_by_add...")
        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )
        first_test_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not first_test_key_value:
            self.fail(f"First {SecureStorageKey.TestKey}'s value could not found.")

        time.sleep(3)

        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )
        last_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not last_key_value:
            self.fail(f"Last {SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(last_key_value["value"], last_key_value["value"])
        self.assertNotEqual(last_key_value["created_at"], first_test_key_value["created_at"])

        self.check_cache()

    def test_aesgcm_encryption_decryption_on_add(self):
        print("test_aesgcm_encryption_decryption_on_add...")
        self.__class__._secure_storage._init_aesgcm_cipher()

        key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not key:
            self.fail(f"{SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        # Is encryption works?
        encrypted_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            decrypt=False,
            use_cache=False
        )
        if not encrypted_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s `decrypt=False` value could not found.")
        self.assertNotEqual(
            encrypted_key_value["value"],
            test_key_value["value"]
        )

        # If encryption works then check decryption
        decrypted_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            decrypt=True,
            use_cache=False
        )
        if not decrypted_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s `decrypt=True` value could not found.")
        self.assertEqual(
            decrypted_key_value["value"],
            test_key_value["value"]
        )

        self.check_cache()

    def test_rsa_encryption_decryption_on_add(self):
        print("test_rsa_encryption_decryption_on_add...")
        self.__class__._secure_storage._init_rsa_cipher()

        public_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PublicPem,
            use_cache=False
        )
        if not public_pem:
            raise NoPublicPemFoundError

        private_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PrivatePem,
            use_cache=False
        )
        if not private_pem:
            raise NoPrivatePemFoundError

        original_value = cast(str, NameGenerator.email_address()[0])
        test_key_value = {
            "value": RSACipher.encrypt_password(original_value, public_pem["value"]),
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        found_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(
            original_value,
            RSACipher.decrypt_password(
                found_key_value["value"],
                private_pem["value"]
            )
        )

        self.check_cache()

    def test_update_key(self):
        print("test_update_key...")
        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )
        first_test_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not first_test_key_value:
            self.fail(f"First {SecureStorageKey.TestKey}'s value could not found.")

        time.sleep(2)

        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.update_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )
        last_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not last_key_value:
            self.fail(f"Last {SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(last_key_value["value"], last_key_value["value"])
        self.assertEqual(last_key_value["created_at"], first_test_key_value["created_at"])
        self.assertGreater(last_key_value["last_updated_at"], first_test_key_value["last_updated_at"])

        self.check_cache()

    def test_update_invalid_key(self):
        print("test_update_invalid_key...")
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            NameGenerator.email_address()[0],
            SecureStorageKeyValueType.AESGCMEncrypted,
        )

        time.sleep(1)

        with self.assertRaises(InvalidSecureStorageKeyError):
            self.__class__._secure_storage.update_key(
                "invalidkey",
                NameGenerator.email_address()[0],
                SecureStorageKeyValueType.AESGCMEncrypted,
            )

    def test_update_illegal_key(self):
        print("test_update_illegal_key...")
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            NameGenerator.email_address()[0],
            SecureStorageKeyValueType.AESGCMEncrypted,
        )

        time.sleep(1)

        with self.assertRaises(IllegalSecureStorageKeyError):
            self.__class__._secure_storage.update_key(
                SECURE_STORAGE_ILLEGAL_ACCESS_KEY_LIST[0],
                NameGenerator.email_address()[0],
                SecureStorageKeyValueType.AESGCMEncrypted,
            )

    def test_update_invalid_key_value_type(self):
        print("test_update_invalid_key_value_type...")
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            NameGenerator.email_address()[0],
            SecureStorageKeyValueType.AESGCMEncrypted,
        )

        time.sleep(1)

        with self.assertRaises(InvalidSecureStorageKeyValueTypeError):
            self.__class__._secure_storage.update_key(
                SecureStorageKey.TestKey,
                NameGenerator.email_address()[0],
                "invalidkeyvaluetype",
            )

    def test_aesgcm_encryption_decryption_on_update(self):
        print("test_aesgcm_encryption_decryption_on_update...")
        self.__class__._secure_storage._init_aesgcm_cipher()

        key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not key:
            self.fail(f"{SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        first_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            first_key_value["value"],
            first_key_value["type"],
        )

        last_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.update_key(
            SecureStorageKey.TestKey,
            last_key_value["value"],
            last_key_value["type"],
        )

        # Is encryption works?
        encrypted_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            decrypt=False,
            use_cache=False
        )
        if not encrypted_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s `decrypt=False` value could not found.")
        self.assertNotEqual(
            encrypted_key_value["value"],
            last_key_value["value"]
        )

        # If encryption works then check decryption
        decrypted_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            decrypt=True,
            use_cache=False
        )
        if not decrypted_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s `decrypt=True` value could not found.")
        self.assertEqual(
            decrypted_key_value["value"],
            last_key_value["value"]
        )

        self.check_cache()

    def test_rsa_encryption_decryption_on_update(self):
        print("test_rsa_encryption_decryption_on_update...")
        self.__class__._secure_storage._init_rsa_cipher()

        public_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PublicPem,
            use_cache=False
        )
        if not public_pem:
            self.fail(f"{SecureStorageKey.PublicPem}'s value could not found.")

        private_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PrivatePem,
            use_cache=False
        )
        if not private_pem:
            self.fail(f"{SecureStorageKey.PrivatePem}'s value could not found.")

        first_original_value = cast(str, NameGenerator.email_address()[0])
        first_key_value = {
            "value": RSACipher.encrypt_password(first_original_value, public_pem["value"]),
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            first_key_value["value"],
            first_key_value["type"],
        )

        last_original_value = cast(str, NameGenerator.email_address()[0])
        last_key_value = {
            "value": RSACipher.encrypt_password(last_original_value, public_pem["value"]),
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.update_key(
            SecureStorageKey.TestKey,
            last_key_value["value"],
            last_key_value["type"],
        )

        found_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(
            last_original_value,
            RSACipher.decrypt_password(
                found_key_value["value"],
                private_pem["value"]
            )
        )

        self.check_cache()

    def test_delete_key(self):
        print("test_delete_key...")
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            NameGenerator.email_address()[0],
            SecureStorageKeyValueType.AESGCMEncrypted,
        )

        self.__class__._secure_storage.delete_key(SecureStorageKey.TestKey)
        found_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        self.assertIsNone(found_key_value)

        # Check cache
        key_values = [
            self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey),
            self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey, use_cache=False),
            self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey),
        ]
        self.assertTrue(all(value is None for value in key_values))

    def test_delete_invalid_key(self):
        print("test_delete_invalid_key...")
        with self.assertRaises(InvalidSecureStorageKeyError):
            self.__class__._secure_storage.delete_key("invalidkey")

    def test_delete_illegal_key(self):
        print("test_delete_illegal_key...")
        with self.assertRaises(IllegalSecureStorageKeyError):
            self.__class__._secure_storage.delete_key(
                SECURE_STORAGE_ILLEGAL_ACCESS_KEY_LIST[0]
            )

    def test_clear(self):
        print("test_clear...")
        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        found_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(found_key_value["value"], test_key_value["value"])
        self.assertEqual(found_key_value["type"], test_key_value["type"])

        # Check Cache
        self.__class__._secure_storage.clear()
        self.assertIsNone(self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey))

    def test_destroy(self):
        print("test_destroy...")
        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        self.__class__._secure_storage.destroy()
        self.assertIsNone(self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey))

        # Check Cache
        self.assertIsNone(self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey))

    def test_aesgcm_rotation(self):
        print("test_aesgcm_rotation...")
        self.__class__._secure_storage._init_aesgcm_cipher()

        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        pre_rotation_aesgcm_key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not pre_rotation_aesgcm_key:
            self.fail(f"Pre-Rotation {SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        aesgcm_rotation_result, _ = self.__class__._secure_storage._rotate_aesgcm_cipher()
        self.assertTrue(aesgcm_rotation_result)

        post_rotation_aesgcm_key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not post_rotation_aesgcm_key:
            self.fail(f"Post-Rotation {SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        # Is rotation really successful?
        self.assertNotEqual(pre_rotation_aesgcm_key["value"], post_rotation_aesgcm_key["value"])

        post_rotation_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            use_cache=False
        )
        if not post_rotation_key_value:
            self.fail(f"Post-Rotation {SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(post_rotation_key_value["value"], test_key_value["value"])
        self.assertEqual(post_rotation_key_value["type"], test_key_value["type"])

    def test_aesgcm_rotation_restoration(self):
        print("test_aesgcm_rotation_restoration...")
        self.__class__._secure_storage._init_aesgcm_cipher()

        test_key_value = {
            "value": NameGenerator.email_address()[0],
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        pre_rotation_restoration_backup = self.__class__._secure_storage._create_backup()

        pre_rotation_aesgcm_key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not pre_rotation_aesgcm_key:
            self.fail(f"Pre-Rotation {SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        aesgcm_rotation_result, aesgcm_restoration_result = self.__class__._secure_storage._rotate_aesgcm_cipher()

        if aesgcm_rotation_result:
            # Is rotation really successful?
            post_rotation_aesgcm_key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
            if not post_rotation_aesgcm_key:
                self.fail(f"Post-Rotation {SecureStorageKey.AESGCMCipherKey}'s value could not found.")
            self.assertNotEqual(pre_rotation_aesgcm_key["value"], post_rotation_aesgcm_key["value"])

            # Imitiate restoration
            self.__class__._secure_storage._load_backup(pre_rotation_restoration_backup)
            aesgcm_restoration_result = self.__class__._secure_storage._restore_aesgcm_cipher()
            self.assertTrue(aesgcm_restoration_result)
        else:
            self.assertTrue(aesgcm_restoration_result)

        # get aesgcm cipher key again after restoration
        post_rotation_aesgcm_key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not post_rotation_aesgcm_key:
            self.fail(f"Post-Rotation {SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        # Is restoration really succesful?
        self.assertEqual(pre_rotation_aesgcm_key["value"], post_rotation_aesgcm_key["value"])

        post_rotation_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            use_cache=False
        )
        if not post_rotation_key_value:
            self.fail(f"Post-Rotation {SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(post_rotation_key_value["value"], test_key_value["value"])
        self.assertEqual(post_rotation_key_value["type"], test_key_value["type"])

    def test_rsa_rotation(self):
        print("test_rsa_rotation...")
        self.__class__._secure_storage._init_rsa_cipher()

        original_value = cast(str, NameGenerator.email_address()[0])

        pre_rotation_public_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PublicPem,
            use_cache=False
        )
        if not pre_rotation_public_pem:
            self.fail(f"Pre-Rotation {SecureStorageKey.PublicPem}'s value could not found.")

        pre_rotation_private_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PrivatePem,
            use_cache=False
        )
        if not pre_rotation_private_pem:
            self.fail(f"Pre-Rotation {SecureStorageKey.PrivatePem}'s value could not found.")

        test_key_value = {
            "value": RSACipher.encrypt_password(original_value, pre_rotation_public_pem["value"]),
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        rsa_rotation_result, _ = self.__class__._secure_storage._rotate_rsa_cipher()
        self.assertTrue(rsa_rotation_result)

        post_rotation_public_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PublicPem,
            use_cache=False
        )
        if not post_rotation_public_pem:
            self.fail(f"Post-Rotation {SecureStorageKey.PublicPem}'s value could not found.")

        post_rotation_private_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PrivatePem,
            use_cache=False
        )
        if not post_rotation_private_pem:
            self.fail(f"Post-Rotation {SecureStorageKey.PrivatePem}'s value could not found.")

        # Is rotation really successful?
        self.assertNotEqual(pre_rotation_public_pem["value"], post_rotation_public_pem["value"])
        self.assertNotEqual(pre_rotation_private_pem["value"], post_rotation_private_pem["value"])

        found_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            use_cache=False
        )
        if not found_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(
            original_value,
            RSACipher.decrypt_password(
                found_key_value["value"],
                post_rotation_private_pem["value"]
            )
        )

    def test_rsa_rotation_restoration(self):
        print("test_rsa_rotation_restoration...")
        self.__class__._secure_storage._init_rsa_cipher()

        original_value = cast(str, NameGenerator.email_address()[0])

        pre_rotation_public_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PublicPem,
            use_cache=False
        )
        if not pre_rotation_public_pem:
            self.fail(f"Pre-Rotation {SecureStorageKey.PublicPem}'s value could not found.")

        pre_rotation_private_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PrivatePem,
            use_cache=False
        )
        if not pre_rotation_private_pem:
            self.fail(f"Pre-Rotation {SecureStorageKey.PrivatePem}'s value could not found.")

        test_key_value = {
            "value": RSACipher.encrypt_password(original_value, pre_rotation_public_pem["value"]),
            "type": SecureStorageKeyValueType.AESGCMEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        pre_rotation_restoration_backup = self.__class__._secure_storage._create_backup()
        rsa_rotation_result, rsa_restoration_result = self.__class__._secure_storage._rotate_rsa_cipher()

        if rsa_rotation_result:
            # Is rotation really successful?
            post_rotation_public_pem = self.__class__._secure_storage.get_key_value(
                SecureStorageKey.PublicPem,
                use_cache=False
            )
            if not post_rotation_public_pem:
                self.fail(f"Post-Rotation {SecureStorageKey.PublicPem}'s value could not found.")

            post_rotation_private_pem = self.__class__._secure_storage.get_key_value(
                SecureStorageKey.PrivatePem,
                use_cache=False
            )
            if not post_rotation_private_pem:
                self.fail(f"Post-Rotation {SecureStorageKey.PrivatePem}'s value could not found.")

            self.assertNotEqual(pre_rotation_public_pem["value"], post_rotation_public_pem["value"])
            self.assertNotEqual(pre_rotation_private_pem["value"], post_rotation_private_pem["value"])

            # Imitiate restoration
            self.__class__._secure_storage._load_backup(pre_rotation_restoration_backup)
            rsa_restoration_result = self.__class__._secure_storage._restore_rsa_cipher()
            self.assertTrue(rsa_restoration_result)
        else:
            self.assertTrue(rsa_restoration_result)

        # get pems again after restoration
        post_rotation_public_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PublicPem,
            use_cache=False
        )
        if not post_rotation_public_pem:
            self.fail(f"Post-Rotation-Restoration {SecureStorageKey.PublicPem}'s value could not found.")

        post_rotation_private_pem = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.PrivatePem,
            use_cache=False
        )
        if not post_rotation_private_pem:
            self.fail(f"Post-Rotation-Restoration {SecureStorageKey.PrivatePem}'s value could not found.")

        # Is restoration really successful?
        self.assertEqual(pre_rotation_public_pem["value"], post_rotation_public_pem["value"])
        self.assertEqual(pre_rotation_private_pem["value"], post_rotation_private_pem["value"])

        found_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            use_cache=False
        )
        if not found_key_value:
            self.fail(f"Post-Rotation-Restoration {SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(
            original_value,
            RSACipher.decrypt_password(
                found_key_value["value"],
                post_rotation_private_pem["value"]
            )
        )

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestSecureStorage`...")
        cls._secure_storage._load_backup(cls._test_backup_id)
        cls._secure_storage._delete_backup(cls._test_backup_id)
