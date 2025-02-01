import unittest
import json

from classes.account_manager import AccountAlreadyExists, AccountDoesNotExists
from utils.name_generator import NameGenerator
from classes.account_manager import *
from classes.secure_storage import RSACipher, SecureStorage

class TestAccountManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestAccountManager`...")
        cls.addClassCleanup(cls.cleanup)

        cls._secure_storage = SecureStorage()
        cls._secure_storage._create_backup()
        cls._account_manager = AccountManager()

        cls._TEST_ACCOUNTS = [
            AccountWithPassword(
                email_address=NameGenerator.email_address(),
                fullname=NameGenerator.fullname(),
                encrypted_password=RSACipher.encrypt_password(
                    NameGenerator.password(),
                    cls._secure_storage.get_key_value(SecureStorageKey.PrivatePem)["value"]
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

        # Şimdi bu testi bir fulleyelim.
        #
        # Tabi bir de imap.py de ki get_emails problemi var dı
        # hatırlarsan UID sequence set çekilmemiş miydi neydi?
        # bu account bittikten sonra ona bir bakılmalı. Genel
        # olarak proje tekrardan test edilebilir.
        self.__class__._account_manager.remove_all()

        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)

        self.assertEqual(
            test_account,
            self.__class__._account_manager.get(test_account)
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

    def test_edit_account(self):
        print("test_edit_account...")
        self.__class__._account_manager.remove_all()

        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)

        new_fullname = NameGenerator().fullname
        self.__class__._account_manager.edit(Account(
            email_address=test_account.email_address,
            fullname=new_fullname
        ))
        edited_account = self.__class__._account_manager.get(test_account.email_address)
        self.assertTrue(edited_account and edited_account.fullname == new_fullname)

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

    def test_prevent_duplicate_by_add(self):
        print("test_prevent_duplicate_by_add...")
        self.__class__._account_manager.remove_all()

        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)

        with self.assertRaises(AccountAlreadyExists):
            test_account = self.__class__._TEST_ACCOUNTS[0]
            self.__class__._account_manager.add(test_account)

    def test_prevent_duplicate_by_edit(self):
        print("test_prevent_duplicate_by_edit...")
        self.__class__._account_manager.remove_all()

        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.add(test_account)

        with self.assertRaises(AccountAlreadyExists):
            edit_account = self.__class__._TEST_ACCOUNTS[1]
            edit_account.email_address = test_account.email_address
            self.__class__._account_manager.edit(edit_account)

    def test_edit_nonexist(self):
        print("test_edit_nonexist...")
        self.__class__._account_manager.remove_all()

        with self.assertRaises(AccountDoesNotExists):
            test_account = self.__class__._TEST_ACCOUNTS[0]
            test_account.fullname = NameGenerator.fullname()
            self.__class__._account_manager.edit(test_account)

    def test_remove_nonexist(self):
        print("test_remove_nonexist...")
        self.__class__._account_manager.remove_all()
        test_account = self.__class__._TEST_ACCOUNTS[0]
        self.__class__._account_manager.remove(test_account)

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestAccountManager`...")
        cls._account_manager.remove_all()
        cls._secure_storage._load_backup()
        cls._secure_storage._delete_backup()
