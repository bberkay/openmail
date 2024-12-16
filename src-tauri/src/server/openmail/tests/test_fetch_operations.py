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
        cls._email = credentials[0]["email"]
        cls._openmail.connect(cls._email, credentials[0]["password"])
        print(f"Connected to {cls._email}...")

        for i in range(3):
            DummyOperator.send_test_email_to_self_and_get_uid(
                cls._openmail,
                EmailToSend(
                    sender=cls._email,
                    receiver=cls._email,
                    subject=NameGenerator.random_subject_with_uuid(),
                    body=NameGenerator.random_body_with_uuid(),
                    cc=cls._email,
                    bcc=cls._email,
                )
            )

    def test_fetch_basic(self):
        print("test_fetch_standard...")

        print(f"Searching emails from {Folder.Inbox}...")
        self.__class__._openmail.imap.search_emails()

        print(f"Fetching emails from {Folder.Inbox}...")
        mailbox = self.__class__._openmail.imap.get_emails(0, 2)
        self.assertEqual(len(mailbox.emails), 3)

    """def test_fetch_basic(self):
        print("test_fetch_standard...")

        print(f"Searching emails from {Folder.Inbox}...")
        self.__class__._openmail.imap.search_emails()

        print(f"Fetching emails from {Folder.Inbox}...")
        mailbox = self.__class__._openmail.imap.get_emails(0, 3)
        self.assertGreater(len(mailbox.emails), 0)"""
