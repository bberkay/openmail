import json
import time
import unittest
from email.message import EmailMessage

from src.modules.openmail import Openmail
from src.modules.openmail.imap import Mark, Folder
from tests.modules.openmail.utils.dummy_operator import DummyOperator
from tests.modules.openmail.utils.name_generator import NameGenerator

class TestEmailOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestEmailOperations`...")
        cls.addClassCleanup(cls.cleanup)

        cls._openmail = Openmail()
        with open("./credentials.json") as credentials:
            credentials = json.load(credentials)
        cls._email = credentials[0]["email"]
        cls._openmail.connect(cls._email, credentials[0]["password"])
        print(f"Connected to {cls._email}...")

        cls._created_test_folders = []
        cls._sent_test_email_uids = []

    def test_save_email_as_draft(self):
        print("test_save_email_as_draft...")
        email = EmailMessage()
        email["From"] = self.__class__._email
        email["To"] = self.__class__._email
        email["Subject"] = NameGenerator.subject()[0]
        email.set_content(NameGenerator.body()[0])

        appenduid = self.__class__._openmail.imap.save_email_as_draft(email)
        self.assertIsNotNone(appenduid)
        self.assertIsNotNone(self.__class__._openmail.imap.is_email_exists(Folder.Drafts, appenduid))

    def test_update_saved_draft(self):
        print("test_update_saved_draft...")
        email = EmailMessage()
        email["From"] = self.__class__._email
        email["To"] = self.__class__._email
        email["Subject"] = NameGenerator.subject()[0]
        email.set_content(NameGenerator.body()[0])

        appenduid = self.__class__._openmail.imap.save_email_as_draft(email)
        self.assertIsNotNone(appenduid)
        self.assertIsNotNone(self.__class__._openmail.imap.is_email_exists(Folder.Drafts, appenduid))

        # Change subject to something that is definitely
        # different than the old one.
        email["Subject"] = NameGenerator.body()[0]
        new_appenduid = self.__class__._openmail.imap.save_email_as_draft(email, appenduid)
        self.assertIsNotNone(self.__class__._openmail.imap.is_email_exists(Folder.Drafts, new_appenduid))
        self.assertIsNone(self.__class__._openmail.imap.is_email_exists(Folder.Drafts, appenduid))

    def test_mark_as_seen_operation(self):
        print("test_mark_as_seen_operation...")

        print(f"Sending new email to mark as seen...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
        self.__class__._sent_test_email_uids.append(uid)

        status, _ = self.__class__._openmail.imap.mark_email(uid, Mark.Seen)
        self.assertTrue(status)
        self.assertIn(
            Mark.Seen,
            self.__class__._openmail.imap.get_email_flags(uid)[0].flags
        )

    def test_mark_as_seen_multiple_email_operation(self):
        print("test_mark_as_seen_multiple_email_operation...")

        print(f"Sending new email to mark as seen...")
        uids = []
        for i in range(1, 4):
            uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
            uids.append(uid)
            self.__class__._sent_test_email_uids.append(uid)

        sequence_set = ",".join(uids)
        status, _ = self.__class__._openmail.imap.mark_email(sequence_set, Mark.Seen)
        self.assertTrue(status)

        email_flags = self.__class__._openmail.imap.get_email_flags(sequence_set)
        for email_flag in email_flags:
            self.assertIn(Mark.Seen, email_flag.flags)

    def test_unmark_as_flagged_operation(self):
        print("test_unmark_as_flagged_operation...")

        print(f"Sending new email to unmark as flagged...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
        self.__class__._sent_test_email_uids.append(uid)

        status, _ = self.__class__._openmail.imap.mark_email(uid, Mark.Flagged)
        self.assertTrue(status)

        status, _ = self.__class__._openmail.imap.unmark_email(uid, Mark.Flagged)
        self.assertTrue(status)
        self.assertNotIn(
            Mark.Flagged,
            self.__class__._openmail.imap.get_email_flags(uid)[0].flags
        )

    def test_unmark_as_flagged_multiple_email_operation(self):
        print("test_unmark_as_flagged_multiple_email_operation...")

        print(f"Sending new email to unmark as flagged...")
        uids = []
        for i in range(1, 4):
            uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
            uids.append(uid)
            self.__class__._sent_test_email_uids.append(uid)

        sequence_set = ",".join(uids)
        status, _ = self.__class__._openmail.imap.mark_email(sequence_set, Mark.Flagged)
        self.assertTrue(status)

        status, _ = self.__class__._openmail.imap.unmark_email(sequence_set, Mark.Flagged)
        self.assertTrue(status)

        email_flags = self.__class__._openmail.imap.get_email_flags(sequence_set)
        for email_flag in email_flags:
            self.assertNotIn(Mark.Flagged, email_flag.flags)

    def test_move_email_operation(self):
        print("test_move_email_operation...")

        print("Creating new folder to move email to...")
        new_folder_name, _ = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(new_folder_name)

        print(f"Sending new email to move to {new_folder_name}...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
        self.__class__._sent_test_email_uids.append(uid)

        print(f"Moving email {uid} to {new_folder_name}...")
        status, _ = self.__class__._openmail.imap.move_email(Folder.Inbox, new_folder_name, uid)
        self.assertTrue(status)

        print("Waiting 2 seconds after move operation")
        time.sleep(2)

        # Check the moved email, it should not be in Inbox anymore.
        self.assertFalse(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))

        # Since the UID changes from folder to folder, find new UID and then check the target folder.
        self.__class__._openmail.imap.search_emails(new_folder_name)
        uid_after_move = self.__class__._openmail.imap.get_emails().emails[0].uid
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(new_folder_name, uid_after_move))

    def test_move_multiple_email_operation(self):
        print("test_move_multiple_email_operation...")

        print("Creating new folder to move email to...")
        new_folder_name, _ = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(new_folder_name)

        print(f"Sending new emails to move to {new_folder_name}...")
        uids = []
        for i in range(1, 4):
            uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
            uids.append(uid)
            self.__class__._sent_test_email_uids.append(uid)

        print(f"Moving email {uids} to {new_folder_name}...")
        sequence_set = ",".join(uids)
        status, _ = self.__class__._openmail.imap.move_email(Folder.Inbox, new_folder_name, sequence_set)
        self.assertTrue(status)

        print("Waiting 2 seconds after move operation")
        time.sleep(2)

        # Check the moved emails, they should not be in Inbox anymore.
        self.assertFalse(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, sequence_set))

        # Since the UIDs changes from folder to folder, find new UIDs and then check the target folder.
        self.__class__._openmail.imap.search_emails(new_folder_name)
        emails = [email.uid for email in self.__class__._openmail.imap.get_emails().emails]
        sequence_set_after_move = ",".join(emails)
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(new_folder_name, sequence_set_after_move))

    def test_copy_email_operation(self):
        print("test_copy_email_operation...")

        print("Creating new folder to copy email to...")
        new_folder_name, _ = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(new_folder_name)

        print(f"Sending new email to copy to {new_folder_name}...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
        self.__class__._sent_test_email_uids.append(uid)

        print(f"Copying email {uid} to {new_folder_name}...")
        status, _ = self.__class__._openmail.imap.copy_email(Folder.Inbox, new_folder_name, uid)
        self.assertTrue(status)

        print("Waiting 2 seconds after copy operation")
        time.sleep(2)

        # Check the copied email, it should not be moved from Inbox.
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))

        # Since the UID changes from folder to folder, find new UID and then check the target folder.
        self.__class__._openmail.imap.search_emails(new_folder_name)
        uid_after_copy = self.__class__._openmail.imap.get_emails().emails[0].uid
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(new_folder_name, uid_after_copy))

    def test_copy_multiple_email_operation(self):
        print("test_copy_multiple_email_operation...")

        print("Creating new folder to copy email to...")
        new_folder_name, _ = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(new_folder_name)

        print(f"Sending new emails to copy to {new_folder_name}...")
        uids = []
        for i in range(1, 4):
            uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
            uids.append(uid)
            self.__class__._sent_test_email_uids.append(uid)

        print(f"Copying email {uids} to {new_folder_name}...")
        sequence_set = ",".join(uids)
        status, _ = self.__class__._openmail.imap.copy_email(Folder.Inbox, new_folder_name, sequence_set)
        self.assertTrue(status)

        print("Waiting 2 seconds after copy operation")
        time.sleep(2)

        # Check the copied emails, they should not be moved from Inbox.
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, sequence_set))

        # Since the UIDs changes from folder to folder, find new UIDs and then check the target folder.
        self.__class__._openmail.imap.search_emails(new_folder_name)
        emails = [email.uid for email in self.__class__._openmail.imap.get_emails().emails]
        sequence_set_after_move = ",".join(emails)
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(new_folder_name, sequence_set_after_move))

    def test_delete_email_operation(self):
        print("test_delete_email_operation...")

        print(f"Sending new email to delete...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
        self.__class__._sent_test_email_uids.append(uid)

        print(f"Deleting email {uid}...")
        status, _ = self.__class__._openmail.imap.delete_email(Folder.Inbox, uid)
        self.assertTrue(status)

        print("Waiting 2 seconds after delete operation")
        time.sleep(2)

        # Check the deleted email, it should not be in Inbox anymore.
        self.assertFalse(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))

    def test_delete_multiple_email_operation(self):
        print("test_delete_multiple_email_operation...")

        print(f"Sending new emails to delete...")
        uids = []
        for i in range(1, 4):
            uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
            uids.append(uid)
            self.__class__._sent_test_email_uids.append(uid)

        print(f"Deleting email {uids}...")
        sequence_set = ",".join(uids)
        status, _ = self.__class__._openmail.imap.delete_email(Folder.Inbox, sequence_set)
        self.assertTrue(status)

        print("Waiting 2 seconds after delete operation")
        time.sleep(2)

        # Check the deleted emails, they should not be in Inbox anymore.
        self.assertFalse(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, sequence_set))

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestEmailOperations`...")
        for folder_name in cls._created_test_folders:
            cls._openmail.imap.delete_folder(folder_name, True)
        if cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, ",".join(sorted(cls._sent_test_email_uids, key=int)))
        cls._openmail.disconnect()
