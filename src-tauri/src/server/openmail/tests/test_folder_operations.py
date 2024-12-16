import json
import unittest

from openmail.imap import IMAPManager
from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator

class TestFolderOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestFolderOperations`...")
        credentials = json.load(open("openmail/tests/credentials.json"))
        cls._email = credentials[0]["email"]
        cls._imap = IMAPManager(cls._email, credentials[0]["password"])

    def test_create_folder_operation(self):
        folder_name = NameGenerator.random_folder_name_with_uuid()

        status, _ = self.__class__._imap.create_folder(folder_name)
        self.assertTrue(status)

    def test_create_folder_with_parent_operation(self):
        print("test_create_folder_with_parent_operation...")
        folder_name, parent_folder_name = NameGenerator.random_folder_name_with_uuid(
            count=2,
            all_different=True
        )

        status, _ = self.__class__._imap.create_folder(folder_name, parent_folder_name)
        self.assertTrue(status)

    def test_create_nonascii_folder_operation(self):
        print("test_create_nonascii_folder_operation...")
        folder_name, parent_folder_name = NameGenerator.random_folder_name_with_uuid(
            "openmail-folder-test-ü-",
            count=2,
            all_different=True
        )

        status, _ = self.__class__._imap.create_folder(folder_name, parent_folder_name)
        self.assertTrue(status)

    def test_move_folder_operation(self):
        print("test_move_folder_operation...")
        folder_name1 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        folder_name2 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        status, _ = self.__class__._imap.move_folder(folder_name1, folder_name2)
        self.assertTrue(status)

    def test_delete_folder_operation(self):
        print("test_delete_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        status, _ = self.__class__._imap.delete_folder(folder_name)
        self.assertTrue(status)

    def test_delete_folder_with_subfolders_operation(self):
        print("test_delete_folder_with_subfolders_operation...")
        _, parent_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, create_parent=True)

        status, _ = self.__class__._imap.delete_folder(parent_folder_name, True)
        self.assertTrue(status)

    def test_rename_folder_operation(self):
        print("test_rename_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        new_folder_name = NameGenerator.random_folder_name_with_uuid()
        status, _ = self.__class__._imap.rename_folder(folder_name, new_folder_name)
        self.assertTrue(status)

    def test_move_nonascii_folder_operation(self):
        print("test_move_nonascii_folder_operation...")
        folder_name1 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ü-")
        folder_name2 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ç-")

        status, _ = self.__class__._imap.move_folder(folder_name1, folder_name2)
        self.assertTrue(status)

    def test_rename_nonascii_folder_operation(self):
        print("test_rename_nonascii_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ü-")

        new_folder_name = NameGenerator.random_folder_name_with_uuid("openmail-folder-test-ç-")
        status, _ = self.__class__._imap.rename_folder(folder_name, new_folder_name)
        self.assertTrue(status)

    @classmethod
    def tearDownClass(cls):
        # TODO: Cleanup
        print("Cleaning up test `TestFolderOperations`...")
        cls._imap.logout()
