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
        credentials = json.load(open("openmail/tests/credentials.json"))
        cls._email = credentials[0]["email"]
        cls._openmail.connect(cls._email, credentials[0]["password"])
        print(f"Connected to {cls._email}...")

    def test_mark_as_seen_operation(self):
        print("test_mark_as_seen_operation...")

        print(f"Creating new email to mark as seen...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        status, _ = self.__class__._openmail.imap.mark_email(Mark.Seen, uid)
        self.assertTrue(status)

    def test_unmark_as_seen_operation(self):
        print("test_unmark_as_seen_operation...")

        print(f"Creating new email to mark as seen...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        status, _ = self.__class__._openmail.imap.mark_email(Mark.Seen, uid)
        self.assertTrue(status)

        status, _ = self.__class__._openmail.imap.unmark_email(Mark.Seen, uid)
        self.assetTrue(status)

    def test_move_email_operation(self):
        print("test_move_email_operation...")

        print("Creating new folder to move email to...")
        new_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        print(f"Creating new email to move to {new_folder_name}...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        print(f"Moving email {uid} to {new_folder_name}...")
        status, _ = self.__class__._openmail.imap.move_email(Folder.Inbox, new_folder_name, uid)
        self.assertTrue(status)

    def test_copy_email_operation(self):
        print("test_copy_email_operation...")

        print("Creating new folder to copy email to...")
        new_folder_name = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        print(f"Creating new email to copy to {new_folder_name}...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        print(f"Copying email {uid} to {new_folder_name}...")
        status, _ = self.__class__._openmail.imap.copy_email(Folder.Inbox, new_folder_name, uid)
        self.assertTrue(status)

    def test_delete_email_operation(self):
        print("test_delete_email_operation...")

        print(f"Creating new email to delete...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)

        print(f"Deleting email {uid}...")
        status, _ = self.__class__._openmail.imap.delete_email(Folder.Inbox, uid)
        self.assertTrue(status)

    @classmethod
    def tearDownClass(cls):
        # TODO: Cleanup
        print("Cleaning up test `TestEmailOperations`...")
        cls._openmail.disconnect()
