import json
import unittest

from openmail import OpenMail
from openmail.imap import Mark, Folder
from openmail.types import EmailToSend, SearchCriteria

from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator
from .utils.sample_file_generator import SampleDocumentGenerator

class TestFetchOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestFetchOperations`...")
        cls._openmail = OpenMail()

        with open("openmail/tests/credentials.json") as credentials:
            credentials = json.load(credentials)

        if len(credentials) < 3:
            raise ValueError("At least 3 credentials are required.")

        cls._sender_email = credentials[0]["email"]
        cls._receiver_emails = [credential["email"] for credential in credentials]
        cls._openmail.connect(cls._sender_email, credentials[0]["password"])
        print(f"Connected to {cls._sender_email}...")

        cls._sent_test_email_uids = []
        cls._created_test_folders = []


    def test_is_sequence_set_valid(self):
        print("test_is_sequence_set_valid...")

        fake_uids = list(map(str, range(1, 21)))

        valid_inputs = [
           "1,2,3",
           "1,2,3,4,5,6,7",
           "1:6:7:9",
           "1,3,4:6:7:9",
           "1,3:6,9,11:13:16,19",
           "2,4:7,9,12:16:19",
           "2,4:7,9,12:*",
           "*:4,5:7"
        ]
        for valid_input in valid_inputs:
            self.assertTrue(self.__class__._openmail.imap._is_sequence_set_valid(valid_input, fake_uids))

        invalid_inputs = [
            "1,2,21,22,23", # There is no 21, 22 and 23 in fake_uids list
            "1,2:*:4,5",
            "1:*:*",
            "1,*",
            "1::*",
            "1::4",
            "*:1:*",
            "1,2,*",
            "1,3,,5:10",
            "1.2.3:5"
        ]
        for invalid_input in invalid_inputs:
            self.assertFalse(self.__class__._openmail.imap._is_sequence_set_valid(invalid_input, fake_uids))

    def test_is_email_exists(self):
        print("test_is_email_exists...")

        new_created_empty_test_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._sender_email)

        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self.assertFalse(self.__class__._openmail.imap.is_email_exists(new_created_empty_test_folder, uid))

        self.__class__._created_test_folders.append(new_created_empty_test_folder)
        self.__class__._sent_test_email_uids.append(uid)

    def test_basic_search(self):
        print("test_basic_search...")

        # Single Receiver, Cc, Bcc, No Attachment
        basic_email = EmailToSend(
            sender=self.__class__._sender_email,
            receiver=self.__class__._receiver_emails[0],
            subject=NameGenerator.random_subject_with_uuid(),
            body=NameGenerator.random_body_with_uuid(),
        )
        basic_email.uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, basic_email)

        self.__class__._openmail.imap.search_emails(search=basic_email.subject)
        mailbox = self.__class__._openmail.imap.get_emails()
        self.assertEqual(len(mailbox.emails), 1)

        self.__class__._sent_test_email_uids.append(basic_email.uid)

    def test_fetch_offset_less_than_zero(self):
        print("test_fetch_simple...")

        print(f"Searching emails from {Folder.Inbox}...")
        self.__class__._openmail.imap.search_emails()

        try:
            print(f"Fetching emails from {Folder.Inbox}...")
            self.__class__._openmail.imap.get_emails(-1, 2)
        except ValueError:
            pass

        try:
            print(f"Fetching emails from {Folder.Inbox}...")
            self.__class__._openmail.imap.get_emails(2, -1)
        except ValueError:
            pass

    def test_search_inbox_folder(self):
        print("test_search_inbox_folder...")

        print(f"Searching emails from {Folder.Inbox}...")
        self.__class__._openmail.imap.search_emails(folder=Folder.Inbox)

        print(f"Fetching emails from {Folder.Sent}...")
        mailbox = self.__class__._openmail.imap.get_emails(0, 2)
        self.assertGreater(len(mailbox.emails), 0)

    def test_search_custom_folder(self):
        print("test_search_custom_folder...")

        print(f"Searching emails from {Folder.Inbox}...")
        self.__class__._openmail.imap.search_emails(folder=self.__class__._custom_folder)

        print(f"Fetching emails from {Folder.Sent}...")
        mailbox = self.__class__._openmail.imap.get_emails(0, 2)
        self.assertGreater(len(mailbox.emails), 0)

    """def test_fetch_basic(self):
        print("test_fetch_standard...")

        print(f"Searching emails from {Folder.Inbox}...")
        self.__class__._openmail.imap.search_emails()

        print(f"Fetching emails from {Folder.Inbox}...")
        mailbox = self.__class__._openmail.imap.get_emails(0, 3)
        self.assertGreater(len(mailbox.emails), 0)"""

    @classmethod
    def tearDownClass(cls):
        print("Cleaning up test `TestFolderOperations`...")
        # TODO: Cleanup
        cls._openmail.disconnect()
