import json
import math
import time
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

        # Send Test Email
        cls._test_sent_basic_email = EmailToSend(
            sender=cls._sender_email,
            receiver=cls._receiver_emails[0],
            subject=NameGenerator.random_subject_with_uuid(),
            body=NameGenerator.random_body_with_uuid(),
        )
        cls._test_sent_basic_email.uid = DummyOperator.send_test_email_to_self_and_get_uid(cls._openmail, cls._sender_email)

        cls._sent_test_email_uids.append(cls._test_sent_basic_email.uid)

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

        self.assertTrue(self.__class__._openmail.imap.is_email_exists(
            Folder.Inbox,
            self.__class__._test_sent_basic_email.uid
        ))
        self.assertFalse(self.__class__._openmail.imap.is_email_exists(
            new_created_empty_test_folder,
            self.__class__._test_sent_basic_email.uid
        ))

        self.__class__._created_test_folders.append(new_created_empty_test_folder)

    def test_basic_search_by_subject(self):
        print("test_basic_search_by_subject...")

        self.__class__._openmail.imap.search_emails(search=self.__class__._test_sent_basic_email.subject)
        mailbox = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(mailbox.emails), 1)

    def test_basic_search_by_body(self):
        print("test_basic_search_by_body...")

        self.__class__._openmail.imap.search_emails(search=self.__class__._test_sent_basic_email.body)
        mailbox = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(mailbox.emails), 1)

    def test_basic_search_by_sender(self):
        print("test_basic_search_by_sender...")

        self.__class__._openmail.imap.search_emails(search=self.__class__._test_sent_basic_email.sender)
        mailbox = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(mailbox.emails), 1)

    def test_basic_search_by_receiver(self):
        print("test_basic_search_by_receiver...")

        self.__class__._openmail.imap.search_emails(search=self.__class__._test_sent_basic_email.receiver)
        mailbox = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(mailbox.emails), 1)

    def test_cc_bcc_search(self):
        print("test_complex_search...")

        # Multiple Receiver, Cc, Bcc, Attachment
        complex_email = EmailToSend(
            sender=self.__class__._sender_email,
            receiver=self.__class__._receiver_emails,
            subject=NameGenerator.random_subject_with_uuid(),
            #cc=self.__class__._receiver_emails[1],
            #bcc=self.__class__._receiver_emails[2],
            body=NameGenerator.random_body_with_uuid(),
            attachments=[SampleDocumentGenerator().as_filepath()]
        )
        complex_email.uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, complex_email)

        """# Cc, Bcc
        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            senders=complex_email.sender,
            receivers=complex_email.receiver,
            subject=complex_email.subject,
            #cc=complex_email.cc,
            #bcc=complex_email.bcc,
        ))
        self.assertEqual(len(self.__class__._openmail.imap.get_emails().emails), 1)"""

        # Include
        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            senders=complex_email.sender,
            receivers=complex_email.receiver,
            subject=complex_email.subject,
            include=complex_email.body
        ))
        self.assertEqual(len(self.__class__._openmail.imap.get_emails().emails), 1)

        # Exclude
        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            subject=complex_email.subject,
            exclude=complex_email.body,
        ))
        self.assertEqual(len(self.__class__._openmail.imap.get_emails().emails), 0)

        # Has attachment
        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            senders=complex_email.sender,
            receivers=complex_email.receiver,
            has_attachments=True
        ))
        self.assertGreaterEqual(len(self.__class__._openmail.imap.get_emails().emails), 1)

        self.__class__._sent_test_email_uids.append(complex_email.uid)

    def test_search_in_custom_folder(self):
        print("test_search_in_custom_folder...")

        new_created_empty_test_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._sender_email)
        self.__class__._openmail.imap.move_email(Folder.Inbox, new_created_empty_test_folder, uid)

        print("Waiting 2 seconds after move operation")
        time.sleep(2)

        self.__class__._openmail.imap.search_emails(folder=new_created_empty_test_folder)
        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertEqual(found_emails.total, 1)

        self.__class__._created_test_folders.append(new_created_empty_test_folder)
        self.__class__._sent_test_email_uids.extend([email.uid for email in found_emails.emails])

    def test_fetch_with_pagination(self):
        print("test_fetch_with_pagination...")

        new_created_empty_test_folder = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)

        uids_list = []
        count = 3
        random_subject_list = []
        for i in range(1, count + 1):
            random_subject = NameGenerator.random_subject_with_uuid()
            uids_list.append(
                DummyOperator.send_test_email_to_self_and_get_uid(
                    self.__class__._openmail,
                    EmailToSend(
                        sender=self.__class__._sender_email,
                        receiver=self.__class__._sender_email,
                        subject=random_subject,
                        body=NameGenerator.random_body_with_uuid()
                    )
                )
            )
            random_subject_list.append(random_subject)

        self.__class__._openmail.imap.copy_email(Folder.Inbox, new_created_empty_test_folder, ",".join(uids_list))

        print("Waiting 2 seconds after copy operation")
        time.sleep(2)

        self.__class__._openmail.imap.search_emails(folder=new_created_empty_test_folder)

        half = math.floor(count / 2)

        one_part_of_emails = self.__class__._openmail.imap.get_emails(0, half)
        self.assertEqual(one_part_of_emails.total, half - 0)
        self.assertEqual([email.subject for email in one_part_of_emails.emails], random_subject_list[:half])

        other_part_of_emails = self.__class__._openmail.imap.get_emails(half, count)
        self.assertEqual(other_part_of_emails.total, count - half)
        self.assertEqual([email.subject for email in other_part_of_emails.emails], random_subject_list[half:count])

        self.__class__._created_test_folders.append(new_created_empty_test_folder)
        self.__class__._sent_test_email_uids.extend(uids_list)

    @classmethod
    def tearDownClass(cls):
        print("Cleaning up test `TestFolderOperations`...")
        for folder_name in cls._created_test_folders:
            cls._openmail.imap.delete_folder(folder_name, True)
        if cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, ",".join(cls._sent_test_email_uids))
        cls._openmail.disconnect()
