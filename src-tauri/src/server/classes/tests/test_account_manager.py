import unittest
import json

from typing import cast

from classes.account_manager import AccountAlreadyExists, AccountDoesNotExists
from classes.tests.utils.name_generator import NameGenerator
from classes.account_manager import *
from classes.secure_storage import NoPublicPemFoundError, RSACipher, SecureStorage, SecureStorageKey

class TestAccountManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestAccountManager`...")
        cls.addClassCleanup(cls.cleanup)

        cls._secure_storage = SecureStorage()
        cls._test_backup_id = cls._secure_storage._create_backup()
        cls._account_manager = AccountManager()

        public_pem = cls._secure_storage.get_key_value(SecureStorageKey.PublicPem)
        if not public_pem:
            raise NoPublicPemFoundError

        cls._TEST_ACCOUNTS = [
            AccountWithPassword(
                email_address=NameGenerator.email_address()[0],
                fullname=NameGenerator.fullname()[0],
                encrypted_password=RSACipher.encrypt_password(
                    NameGenerator.password()[0],
                    public_pem["value"]
                )
            )
            for i in range(1, 10)
        ]

    def test_is_exists(self):
        print("test_is_exists...")
        self.__class__._account_manager.remove_all()

        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.remove(test_account.email_address)
        self.assertFalse(self.__class__._account_manager.is_exists(test_account.email_address))

        self.__class__._account_manager.add(test_account)
        self.assertTrue(self.__class__._account_manager.is_exists(test_account.email_address))

    def test_get_account(self):
        print("test_get_account...")

        self.__class__._account_manager.remove_all()

        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)
        self.assertEqual(
            test_account,
            self.__class__._account_manager.get(test_account.email_address)
        )

    def test_get_some_accounts(self):
        print("test_get_some_accounts...")
        self.__class__._account_manager.remove_all()

        for test_account in self.__class__._TEST_ACCOUNTS[2:5]:
            self.__class__._account_manager.add(test_account)

        self.assertCountEqual(
            self.__class__._TEST_ACCOUNTS[2:5],
            self.__class__._account_manager.get_some(
                [test_account.email_address for test_account in self.__class__._TEST_ACCOUNTS[2:5]]
            )
        )

    def test_get_all_accounts(self):
        print("test_get_all_accounts...")
        self.__class__._account_manager.remove_all()

        for test_account in self.__class__._TEST_ACCOUNTS:
            self.__class__._account_manager.add(test_account)

        self.assertCountEqual(
            self.__class__._TEST_ACCOUNTS,
            self.__class__._account_manager.get_all()
        )

    def test_add_account(self):
        print("test_add_account...")
        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)

        self.assertIn(
            test_account,
            self.__class__._account_manager.get_all()
        )

        accounts = self.__class__._account_manager.get_all()
        self.assertEqual(
            len(set(account.email_address for account in accounts)),
            len([account.email_address for account in accounts])
        )

    def test_edit_account(self):
        print("test_edit_account...")
        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)

        new_fullname = NameGenerator().fullname()
        self.__class__._account_manager.edit(Account(
            email_address=test_account.email_address,
            fullname=new_fullname
        ))
        edited_account = self.__class__._account_manager.get(test_account.email_address)
        self.assertTrue(edited_account and edited_account.fullname == new_fullname)

        accounts = self.__class__._account_manager.get_all()
        self.assertEqual(
            len(set(account.email_address for account in accounts)),
            len([account.email_address for account in accounts])
        )

    def test_remove_account(self):
        print("test_remove_account...")
        self.__class__._account_manager.remove_all()

        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)

        self.__class__._account_manager.remove(test_account.email_address)
        self.assertFalse(self.__class__._account_manager.is_exists(test_account.email_address))

    def test_remove_all_accounts(self):
        print("test_remove_all_accounts...")
        self.__class__._account_manager.remove_all()
        self.assertEqual(len(self.__class__._account_manager.get_all()), 0)

    def test_prevent_duplicate(self):
        print("test_prevent_duplicate...")
        self.__class__._account_manager.remove_all()

        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)

        with self.assertRaises(AccountAlreadyExists):
            test_account = self.__class__._TEST_ACCOUNTS[0]
            self.__class__._account_manager.add(test_account)

    def test_edit_nonexists(self):
        print("test_edit_nonexists...")
        self.__class__._account_manager.remove_all()

        with self.assertRaises(AccountDoesNotExists):
            test_account = self.__class__._TEST_ACCOUNTS[0]
            test_account.fullname = NameGenerator.fullname()[0]
            self.__class__._account_manager.edit(test_account)

    def test_remove_nonexists(self):
        print("test_remove_nonexists...")
        self.__class__._account_manager.remove_all()
        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.remove(test_account)

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestAccountManager`...")
        cls._account_manager.remove_all()
        cls._secure_storage._load_backup(cls._test_backup_id)
        cls._secure_storage._delete_backup(cls._test_backup_id)
