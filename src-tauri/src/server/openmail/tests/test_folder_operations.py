import json
import unittest
import bisect

from openmail import OpenMail
from openmail.imap import FOLDER_LIST
from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator

class TestFolderOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestFolderOperations`...")
        cls.addClassCleanup(cls.cleanup)

        cls._openmail = OpenMail()

        with open("openmail/tests/credentials.json") as credentials:
            credentials = json.load(credentials)

        cls._email = credentials[0]["email"]
        cls._openmail.connect(cls._email, credentials[0]["password"])
        print(f"Connected to {cls._email}...")

        cls._created_test_folders = []

    def test_get_folders_operation(self):
        print("test_get_folders_operation...")

        random_folder_names = []
        for i in range(1, 11):
            bisect.insort(random_folder_names, NameGenerator.random_folder_name_with_uuid())

        folder_structure = [
            f"{random_folder_names[0]}",
            f"{random_folder_names[0]}/{random_folder_names[1]}",
            f"{random_folder_names[0]}/{random_folder_names[1]}/{random_folder_names[2]}",
            f"{random_folder_names[0]}/{random_folder_names[1]}/{random_folder_names[2]}/{random_folder_names[3]}",
            f"{random_folder_names[4]}",
            f"{random_folder_names[4]}/{random_folder_names[5]}",
            f"{random_folder_names[6]}",
            f"{random_folder_names[7]}",
            f"{random_folder_names[7]}/{random_folder_names[8]}",
            f"{random_folder_names[7]}/{random_folder_names[8]}/{random_folder_names[9]}"
        ]

        for folder in folder_structure:
            parent_folder_name, folder_name = folder.rsplit("/", 1) if "/" in folder else (None, folder)
            self.__class__._openmail.imap.create_folder(folder_name, parent_folder_name)

        self.__class__._created_test_folders.extend([folder for folder in folder_structure if "/" not in folder])

        folders = self.__class__._openmail.imap.get_folders()

        # Standard Folders like INBOX, JUNK, TRASH
        self.assertTrue(any(folder.lower() in FOLDER_LIST for folder in folders))

        # Custom Folders
        self.assertListEqual(
            [folder for folder in folders if folder.split("/")[0] in random_folder_names],
            folder_structure
        )

    def test_get_subfolders_operation(self):
        print("test_get_subfolders_operation...")
        new_folder_name, parent_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, create_parent=True)
        self.__class__._created_test_folders.append(parent_folder_name)

        subfolders = self.__class__._openmail.imap.get_folders(parent_folder_name)
        self.assertListEqual(subfolders, [f"{parent_folder_name}/{new_folder_name}"])

    def test_get_folders_as_tagged_operation(self):
        print("test_get_folders_as_tagged_operation...")
        folders = self.__class__._openmail.imap.get_folders(tagged=True)
        self.assertTrue(any(folder.split(":")[0].lower() in FOLDER_LIST for folder in folders if len(folder.split(":")) > 1))

    def test_get_folders_as_not_tagged_operation(self):
        print("test_get_folders_as_not_tagged_operation...")
        folders = self.__class__._openmail.imap.get_folders(tagged=False)
        self.assertFalse(any(folder.split(":")[0].lower() in FOLDER_LIST for folder in folders if len(folder.split(":")) > 1))

    def test_create_folder_operation(self):
        print("test_create_folder_operation...")
        folder_name = NameGenerator.random_folder_name_with_uuid()

        status, msg = self.__class__._openmail.imap.create_folder(folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(folder_name)

        self.assertIn(
            folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_create_folder_with_parent_operation(self):
        print("test_create_folder_with_parent_operation...")
        folder_name, parent_folder_name = NameGenerator.random_folder_name_with_uuid(
            count=2,
            all_different=True
        )

        status, msg = self.__class__._openmail.imap.create_folder(folder_name, parent_folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(created_folder_name)

        created_folder_name = f"{parent_folder_name}/{folder_name}"
        self.assertIn(
            created_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_create_nonascii_folder_operation(self):
        print("test_create_nonascii_folder_operation...")
        folder_name, parent_folder_name = NameGenerator.random_folder_name_with_uuid(
            "openmail-folder-test-ü-",
            count=2,
            all_different=True
        )

        status, msg = self.__class__._openmail.imap.create_folder(folder_name, parent_folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(created_folder_name)

        created_folder_name = f"{parent_folder_name}/{folder_name}"
        self.assertIn(
            created_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_move_folder_operation(self):
        print("test_move_folder_operation...")
        folder_name1 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        folder_name2 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(folder_name1)

        status, msg = self.__class__._openmail.imap.move_folder(folder_name1, folder_name2)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(folder_name2)

        moved_folder_name = f"{folder_name2}/{folder_name1}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_move_folder_with_subfolders_operation(self):
        print("test_move_folder_with_subfolders_operation...")
        _, parent_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-", create_parent=True)
        target_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-")
        self.__class__._created_test_folders.append(parent_folder)

        status, msg = self.__class__._openmail.imap.move_folder(parent_folder, target_folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(target_folder_name)

        moved_folder_name = f"{target_folder_name}/{parent_folder}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )
        self.assertFalse(len(self.__class__._openmail.imap.get_folders(moved_folder_name)) == 0)

    def test_move_child_folder_operation(self):
        print("test_move_child_folder_operation...")
        folder_name, parent_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-", create_parent=True)
        target_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-")
        self.__class__._created_test_folders.append(parent_folder)

        status, msg = self.__class__._openmail.imap.move_folder(f"{parent_folder}/{folder_name}", target_folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(target_folder_name)

        moved_folder_name = f"{target_folder_name}/{folder_name}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_move_child_folder_to_another_parent_folder_operation(self):
        print("test_move_child_folder_to_another_parent_folder_operation...")
        folder_name, parent_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-", create_parent=True)
        target_folder_name, parent_target_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-inner-", create_parent=True)
        self.__class__._created_test_folders.append(parent_folder)

        status, msg = self.__class__._openmail.imap.move_folder(f"{parent_folder}/{folder_name}", f"{parent_target_folder_name}/{target_folder_name}")

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(parent_target_folder_name)

        moved_folder_name = f"{parent_target_folder_name}/{target_folder_name}/{folder_name}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_move_nonascii_folder_operation(self):
        print("test_move_nonascii_folder_operation...")
        folder_name1 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ü-")
        folder_name2 = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ç-")
        self.__class__._created_test_folders.append(folder_name1)

        status, msg = self.__class__._openmail.imap.move_folder(folder_name1, folder_name2)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(folder_name2)

        moved_folder_name = f"{folder_name2}/{folder_name1}"
        self.assertIn(
            moved_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_delete_folder_operation(self):
        print("test_delete_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(folder_name)

        status, msg = self.__class__._openmail.imap.delete_folder(folder_name)
        self.assertTrue(status, msg)
        self.assertNotIn(
            folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_delete_folder_with_subfolders_operation(self):
        print("test_delete_folder_with_subfolders_operation...")
        _, parent_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, create_parent=True)
        self.__class__._created_test_folders.append(parent_folder_name)

        status, msg = self.__class__._openmail.imap.delete_folder(parent_folder_name, True)
        self.assertTrue(status, msg)
        self.assertNotIn(
            parent_folder_name,
            self.__class__._openmail.imap.get_folders()
        )

    def test_rename_folder_operation(self):
        print("test_rename_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(folder_name)

        new_folder_name = NameGenerator.random_folder_name_with_uuid()
        status, msg = self.__class__._openmail.imap.rename_folder(folder_name, new_folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(new_folder_name)

        folders = self.__class__._openmail.imap.get_folders()
        self.assertNotIn(folder_name, folders)
        self.assertIn(new_folder_name, folders)

    def test_rename_child_folder_operation(self):
        print("test_rename_child_folder_operation...")
        folder_name, parent_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, create_parent=True)
        self.__class__._created_test_folders.append(parent_folder_name)

        new_folder_name = NameGenerator.random_folder_name_with_uuid()
        status, msg = self.__class__._openmail.imap.rename_folder(f"{parent_folder_name}/{folder_name}", new_folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(new_folder_name)

        folders = self.__class__._openmail.imap.get_folders()
        old_folder_name = f"{parent_folder_name}/{folder_name}"
        new_folder_name = f"{parent_folder_name}/{new_folder_name}"
        self.assertNotIn(old_folder_name, folders)
        self.assertIn(new_folder_name, folders)

    def test_rename_folder_with_subfolders_operation(self):
        print("test_rename_folder_with_subfolders_operation...")
        _, parent_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, create_parent=True)
        self.__class__._created_test_folders.append(parent_folder_name)

        new_parent_folder_name = NameGenerator.random_folder_name_with_uuid()
        status, msg = self.__class__._openmail.imap.rename_folder(parent_folder_name, new_parent_folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(new_parent_folder_name)

        folders = self.__class__._openmail.imap.get_folders()
        self.assertIn(new_parent_folder_name, folders)
        self.assertNotIn(parent_folder_name, folders)

    def test_rename_nonascii_folder_operation(self):
        print("test_rename_nonascii_folder_operation...")
        folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail, "openmail-folder-test-ü-")
        self.__class__._created_test_folders.append(folder_name)

        new_folder_name = NameGenerator.random_folder_name_with_uuid("openmail-folder-test-ç-")
        status, msg = self.__class__._openmail.imap.rename_folder(folder_name, new_folder_name)

        self.assertTrue(status, msg)
        self.__class__._created_test_folders.append(new_folder_name)

        folders = self.__class__._openmail.imap.get_folders()
        self.assertIn(new_folder_name, folders)
        self.assertNotIn(folder_name, folders)

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestFolderOperations`...")
        for folder_name in cls._created_test_folders:
            cls._openmail.imap.delete_folder(folder_name, True)
        cls._openmail.disconnect()
