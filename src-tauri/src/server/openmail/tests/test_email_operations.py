import json
import unittest

from openmail import OpenMail
from openmail.imap import Mark, Folder
from .utils.dummy_operator import DummyOperator

class TestEmailOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestEmailOperations`...")
        cls._openmail = OpenMail()
        with open("openmail/tests/credentials.json") as credentials:
            credentials = json.load(credentials)
        cls._email = credentials[0]["email"]
        cls._openmail.connect(cls._email, credentials[0]["password"])
        print(f"Connected to {cls._email}...")

        cls._created_test_folders = []
        cls._sent_test_email_uids = []

    def test_mark_as_seen_operation(self):
        print("test_mark_as_seen_operation...")

        print(f"Creating new email to mark as seen...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        status, _ = self.__class__._openmail.imap.mark_email(Mark.Seen, uid)
        self.assertTrue(status)
        self.assertIn(
            Mark.Seen,
            self.__class__._openmail.imap.get_email_flags(uid)[0].flags
        )

        self.__class__._sent_test_email_uids.append(uid)

    def test_unmark_as_seen_operation(self):
        print("test_unmark_as_seen_operation...")

        print(f"Creating new email to mark as seen...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        status, _ = self.__class__._openmail.imap.mark_email(Mark.Seen, uid)
        self.assertTrue(status)

        status, _ = self.__class__._openmail.imap.unmark_email(Mark.Seen, uid)
        self.assetTrue(status)
        self.assertNotIn(
            Mark.Seen,
            self.__class__._openmail.imap.get_email_flags(uid)[0].flags
        )
        print("uid eklenecek: ", uid)
        self.__class__._sent_test_email_uids.append(uid)
        print("aasdasdazxc: ", self.__class__._sent_test_email_uids)

    def test_move_email_operation(self):
        print("test_move_email_operation...")

        print("Creating new folder to move email to...")
        new_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        print(f"Creating new email to move to {new_folder_name}...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        print(f"Moving email {uid} to {new_folder_name}...")
        status, _ = self.__class__._openmail.imap.move_email(Folder.Inbox, new_folder_name, uid)
        self.assertTrue(status)
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(new_folder_name, uid))
        self.assertFalse(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))

        self.__class__._created_test_folders.append(new_folder_name)

    def test_copy_email_operation(self):
        print("test_copy_email_operation...")

        print("Creating new folder to copy email to...")
        new_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        print(f"Creating new email to copy to {new_folder_name}...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        print(f"Copying email {uid} to {new_folder_name}...")
        status, _ = self.__class__._openmail.imap.copy_email(Folder.Inbox, new_folder_name, uid)
        self.assertTrue(status)
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(new_folder_name, uid))
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))

        self.__class__._created_test_folders.append(new_folder_name)
        self.__class__._sent_test_email_uids.append(uid)

    def test_delete_email_operation(self):
        print("test_delete_email_operation...")

        print(f"Creating new email to delete...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        print(f"Deleting email {uid}...")
        status, _ = self.__class__._openmail.imap.delete_email(Folder.Inbox, uid)
        self.assertTrue(status)

        self.__class__._sent_test_email_uids.append(uid)

    @classmethod
    def tearDownClass(cls):
        print("Cleaning up test `TestEmailOperations`...")
        for folder_name in cls._created_test_folders:
            cls._openmail.imap.delete_folder(folder_name, True)
        print("uid list:", ",".join(cls._sent_test_email_uids))
        cls._openmail.imap.delete_email(Folder.Inbox, ",".join(cls._sent_test_email_uids))
        cls._openmail.disconnect()
