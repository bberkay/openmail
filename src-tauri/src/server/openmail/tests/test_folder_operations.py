import json
import unittest

from openmail import OpenMail
from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator

class TestFolderOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestFolderOperations`...")
        cls._openmail = OpenMail()

        with open("openmail/tests/credentials.json") as credentials:
            credentials = json.load(credentials)

        cls._email = credentials[0]["email"]
        cls._openmail.connect(cls._email, credentials[0]["password"])
        print(f"Connected to {cls._email}...")

        cls._created_test_folders = []

    def test_create_folder_operation(self):
        folder_name = NameGenerator.random_folder_name_with_uuid()

        status, msg = self.__class__._openmail.imap.create_folder(folder_name)
        self.assertTrue(status, msg)
        self.assertIn(
            folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(folder_name)

    def test_create_folder_with_parent_operation(self):
        print("test_create_folder_with_parent_operation...")
        folder_name, parent_folder_name = NameGenerator.random_folder_name_with_uuid(
            count=2,
            all_different=True
        )

        status, msg = self.__class__._openmail.imap.create_folder(folder_name, parent_folder_name)
        self.assertTrue(status, msg)

        created_folder_name = f"{parent_folder_name}/{folder_name}"
        self.assertIn(
            created_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(created_folder_name)

    def test_create_nonascii_folder_operation(self):
        print("test_create_nonascii_folder_operation...")
        folder_name, parent_folder_name = NameGenerator.random_folder_name_with_uuid(
            "openmail-folder-test-ü-",
            count=2,
            all_different=True
        )

        status, msg = self.__class__._openmail.imap.create_folder(folder_name, parent_folder_name)
        self.assertTrue(status, msg)

        created_folder_name = f"{parent_folder_name}/{folder_name}"
        self.assertIn(
            created_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(created_folder_name)

    def test_move_folder_operation(self):
        print("test_move_folder_operation...")
        folder_name1 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        folder_name2 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        status, msg = self.__class__._openmail.imap.move_folder(folder_name1, folder_name2)
        self.assertTrue(status, msg)

        moved_folder_name = f"{folder_name2}/{folder_name1}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(folder_name1, folder_name2)

    def test_move_folder_with_subfolders_operation(self):
        print("test_move_folder_with_subfolders_operation...")
        _, parent_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-", create_parent=True)
        target_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-")

        status, msg = self.__class__._openmail.imap.move_folder(parent_folder, target_folder_name)
        self.assertTrue(status, msg)

        moved_folder_name = f"{target_folder_name}/{parent_folder}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )
        self.assertFalse(len(self.__class__._openmail.imap.get_folders(moved_folder_name)) == 0)

        self.__class__._created_test_folders.append(parent_folder, target_folder_name)

    def test_move_child_folder_operation(self):
        print("test_move_child_folder_operation...")
        folder_name, parent_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-", create_parent=True)
        target_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-")

        status, msg = self.__class__._openmail.imap.move_folder(f"{parent_folder}/{folder_name}", target_folder_name)
        self.assertTrue(status, msg)

        moved_folder_name = f"{target_folder_name}/{folder_name}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(parent_folder, target_folder_name)

    def test_move_child_folder_to_another_parent_folder_operation(self):
        print("test_move_child_folder_to_another_parent_folder_operation...")
        folder_name, parent_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-", create_parent=True)
        target_folder_name, parent_target_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-", create_parent=True)

        status, msg = self.__class__._openmail.imap.move_folder(f"{parent_folder}/{folder_name}", f"{parent_target_folder_name}/{target_folder_name}")
        self.assertTrue(status, msg)

        moved_folder_name = f"{parent_target_folder_name}/{target_folder_name}/{folder_name}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(parent_folder, parent_target_folder_name)

    def test_move_nonascii_folder_operation(self):
        print("test_move_nonascii_folder_operation...")
        folder_name1 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ü-")
        folder_name2 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ç-")

        status, msg = self.__class__._openmail.imap.move_folder(folder_name1, folder_name2)
        self.assertTrue(status, msg)

        moved_folder_name = f"{folder_name2}/{folder_name1}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(folder_name1, folder_name2)

    def test_delete_folder_operation(self):
        print("test_delete_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        status, msg = self.__class__._openmail.imap.delete_folder(folder_name)
        self.assertTrue(status, msg)
        self.assertNotIn(
            folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(folder_name)

    def test_delete_folder_with_subfolders_operation(self):
        print("test_delete_folder_with_subfolders_operation...")
        _, parent_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, create_parent=True)

        status, msg = self.__class__._openmail.imap.delete_folder(parent_folder_name)
        self.assertTrue(status, msg)
        self.assertNotIn(
            parent_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

        self.__class__._created_test_folders.append(parent_folder_name)

    def test_rename_folder_operation(self):
        print("test_rename_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        new_folder_name = NameGenerator.random_folder_name_with_uuid()
        status, msg = self.__class__._openmail.imap.rename_folder(folder_name, new_folder_name)
        self.assertTrue(status, msg)

        folders = self.__class__._openmail.imap.get_folders()
        self.assertNotIn(folder_name, folders)
        self.assertIn(new_folder_name, folders)

        self.__class__._created_test_folders.append(folder_name, new_folder_name)

    def test_rename_child_folder_operation(self):
        print("test_rename_child_folder_operation...")
        folder_name, parent_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, create_parent=True)

        new_folder_name = NameGenerator.random_folder_name_with_uuid()
        status, msg = self.__class__._openmail.imap.rename_folder(f"{parent_folder_name}/{folder_name}", new_folder_name)
        self.assertTrue(status, msg)

        folders = self.__class__._openmail.imap.get_folders()
        old_folder_name = f"{parent_folder_name}/{folder_name}"
        new_folder_name = f"{parent_folder_name}/{new_folder_name}"
        self.assertNotIn(old_folder_name, folders)
        self.assertIn(new_folder_name, folders)

        self.__class__._created_test_folders.append(parent_folder_name, new_folder_name)

    def test_rename_folder_with_subfolders_operation(self):
        print("test_rename_folder_with_subfolders_operation...")
        _, parent_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, create_parent=True)

        new_parent_folder_name = NameGenerator.random_folder_name_with_uuid()
        status, msg = self.__class__._openmail.imap.rename_folder(parent_folder_name, new_parent_folder_name)
        self.assertTrue(status, msg)

        folders = self.__class__._openmail.imap.get_folders()
        self.assertIn(new_parent_folder_name, folders)
        self.assertNotIn(parent_folder_name, folders)

        self.__class__._created_test_folders.append(parent_folder_name, new_parent_folder_name)

    def test_rename_nonascii_folder_operation(self):
        print("test_rename_nonascii_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ü-")

        new_folder_name = NameGenerator.random_folder_name_with_uuid("openmail-folder-test-ç-")
        status, msg = self.__class__._openmail.imap.rename_folder(folder_name, new_folder_name)
        self.assertTrue(status, msg)

        folders = self.__class__._openmail.imap.get_folders()
        self.assertIn(new_folder_name, folders)
        self.assertNotIn(folder_name, folders)

        self.__class__._created_test_folders.append(folder_name, new_folder_name)

    @classmethod
    def tearDownClass(cls):
        print("Cleaning up test `TestFolderOperations`...")
        for folder_name in cls._created_test_folders:
            cls._openmail.imap.delete_folder(folder_name, True)
        cls._openmail.disconnect()
