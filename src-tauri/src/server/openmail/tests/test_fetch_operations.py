import json
import unittest

from openmail import OpenMail
from openmail.imap import Mark, Folder
from openmail.types import EmailToSend

from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator

class TestFetchOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestFetchOperations`...")
        cls._openmail = OpenMail()
        credentials = json.load(open("openmail/tests/credentials.json"))
        if len(credentials) < 3:
            raise ValueError("At least 3 credentials are required.")

        cls._sender_email = credentials[0]["email"]
        cls._receiver_emails = [credential["email"] for credential in credentials[1:]]
        cls._openmail.connect(cls._sender_email, credentials[0]["password"])
        print(f"Connected to {cls._sender_email}...")

        cls._sent_emails: list[EmailToSend] = [

        ]

        cls._simple_email = EmailToSend(
            sender=cls._sender_email,
            receiver=cls._receiver_emails,
            subject=NameGenerator.random_subject_with_uuid(),
            body=NameGenerator.random_body_with_uuid(),
            cc=cls._email,
            bcc=cls._email,
        )
        cls._simple_email.uid = DummyOperator.send_test_email_to_self_and_get_uid(
            cls._openmail,
            cls._sent_simple_mail
        )

        cls._attachment_email = EmailToSend(
            sender=cls._sender_email,
            receiver=cls._receiver_emails,
            subject=NameGenerator.random_subject_with_uuid(),
            body=NameGenerator.random_body_with_uuid(),
            cc=cls._email,
            bcc=cls._email,
        )
        cls._attachment_email_uid = DummyOperator.send_test_email_to_self_and_get_uid(
            cls._openmail,
            cls._sent_attachment_mail
        )

        cls._sent_email_uids.append(single_receiver_uid, multiple_receivers_uid)

        cls._custom_test_folder_name = DummyOperator.create_test_folder_and_get_name(
            cls._openmail
        )

    def test_search_and_fetch_simple(self):
        print("test_fetch_simple...")

        print(f"Searching emails from {Folder.Inbox}...")
        self.__class__._openmail.imap.search_emails()

        print(f"Fetching emails from {Folder.Inbox}...")
        mailbox = self.__class__._openmail.imap.get_emails(0, 2)
        self.assertEqual(len(mailbox.emails), 3)

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
