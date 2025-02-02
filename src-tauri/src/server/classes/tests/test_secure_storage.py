import time
import unittest
import json
from typing import cast

from classes.secure_storage import *

class TestSecureStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestSecureStorage`...")
        cls.addClassCleanup(cls.cleanup)
        cls._secure_storage = SecureStorage()
        cls._secure_storage._create_backup()

    def check_cache(self):
        print("Checking Cache...")
        key_values = [
            self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey, decrypt=False),
            self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey, use_cache=False, decrypt=False),
            self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey),
        ]
        self.assertEqual(
            len(key_values),
            [key_value["value"] for key_value in key_values if key_value]
        )
        self.assertEqual(
            len(set([key_value["value"] for key_value in key_values if key_value])),
            1
        )

    def test_get_key_value(self):
        print("test_get_key_value...")
        test_key_value = {
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
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

    def test_add_key(self):
        print("test_add_key...")
        test_key_value = {
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
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

    def test_add_nonexists_key(self):
        print("test_add_nonexists_key...")
        with self.assertRaises(InvalidSecureStorageKeyError):
            self.__class__._secure_storage.add_key(
                "nonexistskey",
                "1234",
                SecureStorageKeyValueType.Plain,
            )

    def test_add_nonexists_key_value_type(self):
        print("test_add_nonexists_key_value_type...")
        with self.assertRaises(InvalidSecureStorageKeyValueTypeError):
            self.__class__._secure_storage.add_key(
                SecureStorageKey.TestKey,
                "1234",
                "nonexistskeyvaluetype",
            )

    def test_override_by_add(self):
        print("test_override_by_add...")
        test_key_value = {
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )
        first_test_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not first_test_key_value:
            self.fail(f"First {SecureStorageKey.TestKey}'s value could not found.")

        time.sleep(5)

        test_key_value = {
            "value": "4567",
            "type": SecureStorageKeyValueType.Plain
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

        aesgcmcipher = AESGCMCipher(bytes.fromhex(key["value"]))

        test_key_value = {
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
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
        self.assertEqual(
            encrypted_key_value["value"],
            aesgcmcipher.encrypt(test_key_value["value"])
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

        original_value = "123"
        test_key_value = {
            "value": RSACipher.encrypt_password(original_value, public_pem["value"]),
            "type": SecureStorageKeyValueType.RSAEncrypted
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
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )
        first_test_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not first_test_key_value:
            self.fail(f"First {SecureStorageKey.TestKey}'s value could not found.")

        time.sleep(5)

        test_key_value = {
            "value": "4567",
            "type": SecureStorageKeyValueType.Plain
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

    def test_aesgcm_encryption_decryption_on_update(self):
        print("test_aesgcm_encryption_decryption_on_update...")
        self.__class__._secure_storage._init_aesgcm_cipher()

        key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not key:
            self.fail(f"{SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        aesgcmcipher = AESGCMCipher(bytes.fromhex(key["value"]))

        first_key_value = {
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            first_key_value["value"],
            first_key_value["type"],
        )

        last_key_value = {
            "value": "8889",
            "type": SecureStorageKeyValueType.Plain
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
        self.assertEqual(
            encrypted_key_value["value"],
            aesgcmcipher.encrypt(last_key_value["value"])
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

        first_original_value = "123"
        first_key_value = {
            "value": RSACipher.encrypt_password(first_original_value, public_pem["value"]),
            "type": SecureStorageKeyValueType.RSAEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            first_key_value["value"],
            first_key_value["type"],
        )

        last_original_value = "8889"
        last_key_value = {
            "value": RSACipher.encrypt_password(last_original_value, public_pem["value"]),
            "type": SecureStorageKeyValueType.RSAEncrypted
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
            "123",
            SecureStorageKeyValueType.Plain,
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

    def test_delete_nonexists_key(self):
        print("test_delete_nonexists_key...")
        with self.assertRaises(InvalidSecureStorageKeyError):
            self.__class__._secure_storage.delete_key("nonexistskey")

    def test_clear(self):
        print("test_clear...")
        test_key_value = {
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        self.__class__._secure_storage.clear()
        found_key_value = self.__class__._secure_storage.get_key_value(SecureStorageKey.TestKey)
        if not found_key_value:
            self.fail(f"{SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(found_key_value["value"], test_key_value["value"])
        self.assertEqual(found_key_value["type"], test_key_value["type"])

        # Check Cache
        self.assertIsNone(self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey))

    def test_destroy(self):
        print("test_destroy...")
        test_key_value = {
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
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
            "value": "123",
            "type": SecureStorageKeyValueType.Plain
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        pre_rotation_aesgcm_key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not pre_rotation_aesgcm_key:
            self.fail(f"Pre-Rotation {SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        self.__class__._secure_storage._rotate_aesgcm_cipher()

        post_rotation_aesgcm_key = self.__class__._secure_storage._get_password(SecureStorageKey.AESGCMCipherKey)
        if not post_rotation_aesgcm_key:
            self.fail(f"Post-Rotation {SecureStorageKey.AESGCMCipherKey}'s value could not found.")

        # Is rotation successful?
        self.assertNotEqual(pre_rotation_aesgcm_key["value"], post_rotation_aesgcm_key["value"])

        post_rotation_aesgcmcipher = AESGCMCipher(bytes.fromhex(post_rotation_aesgcm_key["value"]))
        post_rotation_key_value = self.__class__._secure_storage.get_key_value(
            SecureStorageKey.TestKey,
            decrypt=False,
            use_cache=False
        )
        if not post_rotation_key_value:
            self.fail(f"Post-Rotation {SecureStorageKey.TestKey}'s value could not found.")

        self.assertEqual(post_rotation_aesgcmcipher.decrypt(post_rotation_key_value["value"]), test_key_value["value"])
        self.assertEqual(post_rotation_key_value["type"], test_key_value["type"])

        # Check Cache
        self.assertIsNone(self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey))

    def test_rsa_rotation(self):
        print("test_rsa_rotation...")
        self.__class__._secure_storage._init_rsa_cipher()

        original_value = "123"

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
            "type": SecureStorageKeyValueType.RSAEncrypted
        }
        self.__class__._secure_storage.add_key(
            SecureStorageKey.TestKey,
            test_key_value["value"],
            test_key_value["type"],
        )

        self.__class__._secure_storage._rotate_rsa_cipher()

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

        # Is rotation successful?
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

        # Check Cache
        self.assertIsNone(self.__class__._secure_storage._cache.get(SecureStorageKey.TestKey))

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestSecureStorage`...")
        cls._secure_storage._load_backup()
        cls._secure_storage._delete_backup()
