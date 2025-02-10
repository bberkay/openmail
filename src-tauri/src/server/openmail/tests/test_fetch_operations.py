import base64
import copy
import os
import json
import math
import re
import time
from typing import cast
import unittest

from openmail import OpenMail
from openmail.imap import Mark, Folder
from openmail.types import Attachment, Draft, SearchCriteria
from openmail.parser import HTMLParser, MessageParser
from openmail.encoder import FileBase64Encoder
from openmail.converter import AttachmentConverter

from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator
from .utils.sample_file_generator import SampleDocumentGenerator, SampleImageGenerator

class TestFetchOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestFetchOperations`...")
        cls.addClassCleanup(cls.cleanup)

        cls._openmail = OpenMail()

        with open("./credentials.json") as credentials:
            credentials = json.load(credentials)

        if len(credentials) < 3:
            raise ValueError("At least 3 credentials are required.")

        cls._sender_email = credentials[0]["email"]
        cls._receiver_emails = [credential["email"] for credential in credentials]
        cls._sent_test_email_uids = []
        cls._created_test_folders = []

        cls._openmail.connect(cls._sender_email, credentials[0]["password"])
        print(f"Connected to {cls._sender_email}...")

        # Send Basic Test Email
        cls._test_sent_basic_email = Draft(
            sender=cls._sender_email,
            receiver=cls._receiver_emails[0],
            subject=NameGenerator.subject()[0],
            body=NameGenerator.body()[0],
        )
        cls._test_sent_basic_email_uid = DummyOperator.send_test_email_to_self_and_get_uid(
            cls._openmail,
            copy.copy(cls._test_sent_basic_email)
        )
        cls._sent_test_email_uids.append(cls._test_sent_basic_email_uid)

        # Send Complex Text Email
        cls._test_sent_complex_email = Draft(
            sender=cls._sender_email,
            receiver=cls._receiver_emails,
            subject=NameGenerator.subject()[0],
            cc=cls._receiver_emails[1:],
            bcc=cls._sender_email,
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    {NameGenerator.body()[0]}
                    <i>test_fetch_email_operation</i>
                    <img src="{SampleImageGenerator().as_filepath()[0]}"/>
                    <hr/>
                </body>
            </html>
            ''',
            attachments=[
                AttachmentConverter.resolve_and_convert(filepath)
                for filepath in SampleImageGenerator().as_filepath(2, True)
            ]
        )
        cls._test_sent_complex_email_uid = DummyOperator.send_test_email_to_self_and_get_uid(
            cls._openmail,
            copy.copy(cls._test_sent_complex_email)
        )
        cls._sent_test_email_uids.append(cls._test_sent_complex_email_uid)

        cls._openmail.imap.mark_email(Mark.Seen, cls._test_sent_complex_email_uid, Folder.Inbox)
        cls._openmail.imap.mark_email(Mark.Flagged, cls._test_sent_complex_email_uid, Folder.Inbox)

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

        new_created_empty_test_folder, _ = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(new_created_empty_test_folder)

        self.assertTrue(self.__class__._openmail.imap.is_email_exists(
            Folder.Inbox,
            cast(str, self.__class__._test_sent_basic_email_uid)
        ))
        self.assertFalse(self.__class__._openmail.imap.is_email_exists(
            new_created_empty_test_folder,
            cast(str, self.__class__._test_sent_basic_email_uid)
        ))

    def test_build_search_criteria_query_multiple_or_with_even_length_lists(self):
        print("test_build_search_criteria_query_multiple_or_with_even_length_lists...")

        self.assertEqual(
            self.__class__._openmail.imap.build_search_criteria_query(
                SearchCriteria(
                    senders=["sender@mail.com"],
                    receivers=["receiver1@mail.com", "receiver2@mail.com"],
                )
            ),
            '(FROM "sender@mail.com") (OR (TO "receiver1@mail.com") (TO "receiver2@mail.com"))'
        )

    def test_build_search_criteria_query_multiple_or_with_odd_length_lists(self):
        print("test_build_search_criteria_query_multiple_or_with_odd_length_lists...")

        self.assertEqual(
            self.__class__._openmail.imap.build_search_criteria_query(
                SearchCriteria(
                    senders=["sender@mail.com"],
                    receivers=["receiver1@mail.com", "receiver2@mail.com", "receiver3@mail.com"]
                )
            ),
            '(FROM "sender@mail.com") (OR (TO "receiver1@mail.com") (OR (TO "receiver2@mail.com") (TO "receiver3@mail.com")))'
        )

    def test_build_search_criteria_query_with_all_criteria_at_once(self):
        print("test_build_search_criteria_query_with_all_criteria_keys...")

        self.assertEqual(
            self.__class__._openmail.imap.build_search_criteria_query(
                SearchCriteria(
                    senders=["sender@mail.com"],
                    receivers=["receiver1@mail.com", "receiver2@mail.com"],
                    cc=["cc1@mail.com", "cc2@mail.com"],
                    bcc=["bcc1@mail.com", "bcc2@mail.com", "bcc3@mail.com"],
                    subject="Hello",
                    include="word",
                    exclude="good bye",
                    larger_than=150, # 150 bytes
                    smaller_than=300, # 300 bytes
                    since="2023-01-01",
                    before="2023-12-31",
                    included_flags=[Mark.Flagged, Mark.Seen, "customflag"],
                    has_attachments=True
                )
            ),
            '(FROM "sender@mail.com") (OR (TO "receiver1@mail.com") (TO "receiver2@mail.com")) ' \
            '(OR (CC "cc1@mail.com") (CC "cc2@mail.com")) (OR (BCC "bcc1@mail.com") ' \
            '(OR (BCC "bcc2@mail.com") (BCC "bcc3@mail.com"))) (SUBJECT "Hello") (SINCE "2023-01-01") ' \
            '(BEFORE "2023-12-31") (BODY "word") (NOT BODY "good bye") FLAGGED SEEN KEYWORD CUSTOMFLAG ' \
            '(TEXT "ATTACHMENT") (LARGER 150) (SMALLER 300)'
        )

    def test_basic_search_with_sender(self):
        print("test_basic_search_with_sender...")

        self.__class__._openmail.imap.search_emails(search=cast(str, self.__class__._test_sent_basic_email.sender))
        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(found_emails.total, 1)
        self.assertIn(self.__class__._test_sent_basic_email.sender, found_emails.emails[0].sender)

    def test_basic_search_with_receiver(self):
        print("test_basic_search_with_receiver...")

        self.__class__._openmail.imap.search_emails(search=cast(str, self.__class__._test_sent_basic_email.receiver))
        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(found_emails.total, 1)
        self.assertIn(self.__class__._test_sent_basic_email.receiver, found_emails.emails[0].receiver)

    def test_basic_search_with_subject(self):
        print("test_basic_search_with_subject...")

        self.__class__._openmail.imap.search_emails(search=self.__class__._test_sent_basic_email.subject)
        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(found_emails.total, 1)
        self.assertIn(self.__class__._test_sent_basic_email.subject, found_emails.emails[0].subject)

    def test_basic_search_with_body(self):
        print("test_basic_search_with_body...")

        self.__class__._openmail.imap.search_emails(search=self.__class__._test_sent_basic_email.body)
        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(found_emails.total, 1)

        email_content = self.__class__._openmail.imap.get_email_content(found_emails.folder, found_emails.emails[0].uid)
        self.assertIn(self.__class__._test_sent_basic_email.body, email_content.body)

    def test_complex_search_with_multiple_receiver(self):
        print("test_complex_search_with_multiple_receiver...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            receivers=cast(list[str], self.__class__._test_sent_complex_email.receiver),
        ))

        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(found_emails.total, 1)

        self.assertCountEqual(
            [email.strip() for email in found_emails.emails[0].receiver.split(",")],
            self.__class__._test_sent_complex_email.receiver
        )

    def test_complex_search_with_cc(self):
        print("test_complex_search_with_cc...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            cc=cast(list[str], self.__class__._test_sent_complex_email.cc),
        ))

        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(found_emails.total, 1)

        email_content = self.__class__._openmail.imap.get_email_content(
            found_emails.folder,
            found_emails.emails[0].uid
        )
        assert email_content.cc
        self.assertCountEqual(
            [email.strip() for email in email_content.cc.split(",")],
            cast(list[str], self.__class__._test_sent_complex_email.cc)
        )

    def test_complex_search_with_bcc(self):
        print("test_complex_search_with_bcc...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            bcc=[cast(str, self.__class__._test_sent_complex_email.bcc)],
        ))

        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(found_emails.total, 1)

        email_content = self.__class__._openmail.imap.get_email_content(
            found_emails.folder,
            found_emails.emails[0].uid
        )
        assert email_content.bcc
        self.assertIn(
            [email.strip() for email in email_content.bcc.split(",")],
            cast(str, self.__class__._test_sent_complex_email.bcc)
        )

    def test_complex_search_with_include(self):
        print("test_complex_search_with_include...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            include=self.__class__._test_sent_complex_email.body
        ))

        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertEqual(found_emails.total, 1)

        email_content = self.__class__._openmail.imap.get_email_content(found_emails.folder, found_emails.emails[0].uid)
        self.assertIn(self.__class__._test_sent_complex_email.body, email_content.body)

    def test_complex_search_with_exclude(self):
        print("test_complex_search_with_exclude...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            exclude=self.__class__._test_sent_basic_email.body
        ))

        found_emails = self.__class__._openmail.imap.get_emails(1, 1)
        self.assertEqual(found_emails.total, 1)

        email_content = self.__class__._openmail.imap.get_email_content(found_emails.folder, found_emails.emails[0].uid)
        self.assertNotIn(self.__class__._test_sent_basic_email.body, email_content.body)

    def test_complex_search_with_attachments(self):
        print("test_complex_search_with_attachments...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            has_attachments=True
        ))

        found_emails = self.__class__._openmail.imap.get_emails(1, 1)
        self.assertEqual(found_emails.total, 1)
        assert found_emails.emails[0].attachments is not None
        self.assertGreaterEqual(len(found_emails.emails[0].attachments), 1)

    def test_complex_search_with_smaller_than(self):
        print("test_complex_search_with_smaller_than...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            smaller_than=30000
        ))

        found_emails = self.__class__._openmail.imap.get_emails(1, 1)
        self.assertEqual(found_emails.total, 1)

        size = self.__class__._openmail.imap.get_email_size(found_emails.folder, found_emails.emails[0].uid)
        assert size is not None
        self.assertLessEqual(size, 30000)

    def test_complex_search_with_larger_than(self):
        print("test_complex_search_with_larger_than...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            larger_than=30000
        ))

        found_emails = self.__class__._openmail.imap.get_emails(1, 1)
        self.assertEqual(found_emails.total, 1)

        size = self.__class__._openmail.imap.get_email_size(found_emails.folder, found_emails.emails[0].uid)
        assert size is not None
        self.assertGreaterEqual(size, 30000)

    def test_complex_search_with_include_flags(self):
        print("test_complex_search_with_include_flags...")

        self.__class__._openmail.imap.search_emails(search=SearchCriteria(
            included_flags=[Mark.Seen, Mark.Flagged]
        ))

        found_emails = self.__class__._openmail.imap.get_emails(1, 1)
        self.assertGreaterEqual(found_emails.total, 1)
        assert found_emails.emails[0].flags is not None
        self.assertIn(Mark.Flagged, found_emails.emails[0].flags)
        self.assertIn(Mark.Seen, found_emails.emails[0].flags)

    def test_get_emails(self):
        print("test_get_emails...")
        self.__class__._openmail.imap.search_emails()
        mailbox = self.__class__._openmail.imap.get_emails()
        self.assertGreater(mailbox.total, 0)
        self.assertEqual(mailbox.folder, Folder.Inbox)
        for email in mailbox.emails:
            self.assertIsNotNone(email.uid)
            self.assertIsNotNone(email.sender)
            self.assertIsNotNone(email.receiver)
            self.assertIsNotNone(email.subject)
            self.assertIsNotNone(email.body)

    def test_get_email_content(self):
        print("test_get_email_content...")

        email_content = self.__class__._openmail.imap.get_email_content(
            Folder.Inbox,
            cast(str, self.__class__._test_sent_complex_email_uid)
        )

        # Recipients
        for key in ["sender", "receiver", "cc"]:
            self.assertCountEqual(
                [email.strip() for email in email_content[key].split(",")],
                (
                    [email.strip() for email in self.__class__._test_sent_complex_email[key].split(",")]
                    if isinstance(self.__class__._test_sent_complex_email[key], str)
                    else self.__class__._test_sent_complex_email[key]
                )
            )

        # Subject
        self.assertEqual(
            email_content.subject,
            self.__class__._test_sent_complex_email.subject
        )

        # Body (and inline attachments if body is html)
        complex_email_body = self.__class__._test_sent_complex_email.body
        if HTMLParser.is_html(complex_email_body):
            # Replace cids in `email_to_send` with base64 data to compare
            # with `email_content`
            inline_srcs = MessageParser.get_inline_attachment_sources(complex_email_body)
            if inline_srcs:
                complex_email_inline_attachments = [match[1] for match in inline_srcs]
                if complex_email_inline_attachments:
                    for complex_email_inline_attachment in complex_email_inline_attachments:
                        if not complex_email_inline_attachment.startswith("data:"):
                            base64_data = FileBase64Encoder.read_file(
                                complex_email_inline_attachment
                            )
                            complex_email_body = complex_email_body.replace(
                                complex_email_inline_attachment,
                                f"data:{base64_data[1]};base64,{base64_data[3]}",
                                count=1
                            )
                    # Clean bodies
                    email_content.body = email_content.body.replace("base64, ", "base64,", count=1)
                    complex_email_body = complex_email_body.replace("base64, ", "base64,", count=1)
                    email_content.body = re.sub(r"\s+", "", email_content.body)
                    complex_email_body = re.sub(r"\s+", "", complex_email_body)

        self.assertMultiLineEqual(
            complex_email_body.strip(),
            email_content.body.strip(),
        )

        # Attachments
        if not self.__class__._test_sent_complex_email.attachments:
            self.fail("There is no attachment in `test_sent_complex_email`.")

        if not "attachments" in email_content.keys() or not email_content.attachments:
            self.fail("There is no attachment in `email_content`")

        self.assertCountEqual(
            [attachment.name for attachment in self.__class__._test_sent_complex_email.attachments],
            [attachment.name for attachment in email_content.attachments]
        )
        for attachment in self.__class__._test_sent_complex_email.attachments:
            found_attachment = self.__class__._openmail.imap.download_attachment(
                Folder.Inbox,
                cast(str, self.__class__._test_sent_complex_email_uid),
                attachment.name,
                attachment.cid or ""
            )

            assert found_attachment is not None
            assert found_attachment.data is not None

            if isinstance(attachment.data, bytes):
                attachment.data = base64.b64encode(attachment.data).decode('utf-8')

            found_attachment.data = found_attachment.data.replace("\r\n", "")

            for field in ["name", "type", "cid", "data"]:
                self.assertEqual(
                    attachment[field],
                    found_attachment[field]
                )

    def test_get_email_flags(self):
        print("test_get_email_flags...")

        self.assertIn(
            Mark.Flagged,
            self.__class__._openmail.imap.get_email_flags(
                cast(str, self.__class__._test_sent_complex_email_uid)
            )[0].flags
        )

    def test_get_email_size(self):
        print("test_get_email_size...")

        self.assertGreater(
            self.__class__._openmail.imap.get_email_size(
                Folder.Inbox,
                cast(str, self.__class__._test_sent_complex_email_uid)
            ) or 0,
            0
        )

    def test_download_attachment(self):
        print("test_download_attachment...")
        if not self.__class__._test_sent_complex_email.attachments:
            self.fail("There is no attachment in `test_sent_complex_email`.")

        email_content = self.__class__._openmail.imap.get_email_content(
            Folder.Inbox,
            cast(str, self.__class__._test_sent_complex_email_uid)
        )

        if not "attachments" in email_content.keys() or not email_content.attachments:
            self.fail("There is no attachment in `email_content`")

        self.assertCountEqual(
            [attachment.name for attachment in self.__class__._test_sent_complex_email.attachments],
            [attachment.name for attachment in email_content.attachments]
        )
        for attachment in self.__class__._test_sent_complex_email.attachments:
            found_attachment = self.__class__._openmail.imap.download_attachment(
                Folder.Inbox,
                cast(str, self.__class__._test_sent_complex_email_uid),
                attachment.name,
                attachment.cid or ""
            )

            assert found_attachment is not None
            assert found_attachment.data is not None

            if isinstance(attachment.data, bytes):
                attachment.data = base64.b64encode(attachment.data).decode('utf-8')

            found_attachment.data = found_attachment.data.replace("\r\n", "")

            for field in ["name", "type", "cid", "data"]:
                self.assertEqual(
                    attachment[field],
                    found_attachment[field]
                )

    def test_search_in_custom_folder(self):
        print("test_search_in_custom_folder...")

        new_created_empty_test_folder, _ = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(new_created_empty_test_folder)

        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._sender_email)
        self.__class__._sent_test_email_uids.append(uid)
        self.__class__._openmail.imap.move_email(Folder.Inbox, new_created_empty_test_folder, uid)

        print("Waiting 2 seconds after move operation")
        time.sleep(2)

        self.__class__._openmail.imap.search_emails(folder=new_created_empty_test_folder)
        found_emails = self.__class__._openmail.imap.get_emails()
        self.assertEqual(found_emails.total, 1)

        self.__class__._sent_test_email_uids.extend([email.uid for email in found_emails.emails])

    def test_fetch_with_pagination(self):
        print("test_fetch_with_pagination...")

        new_created_empty_test_folder, _ = DummyOperator.create_test_folder_and_get_name(self.__class__._openmail)
        self.__class__._created_test_folders.append(new_created_empty_test_folder)

        uids_list = []
        count = 3
        random_subject_list = []
        for i in range(1, count + 1):
            random_subject = NameGenerator.subject()[0]
            uid = DummyOperator.send_test_email_to_self_and_get_uid(
                self.__class__._openmail,
                Draft(
                    sender=self.__class__._sender_email,
                    receiver=self.__class__._sender_email,
                    subject=random_subject,
                    body=NameGenerator.body()[0]
                )
            )
            uids_list.append(uid)
            self.__class__._sent_test_email_uids.append(uid)
            random_subject_list.append(random_subject)

        self.__class__._openmail.imap.copy_email(Folder.Inbox, new_created_empty_test_folder, ",".join(uids_list))

        print("Waiting 2 seconds after copy operation")
        time.sleep(2)

        self.__class__._openmail.imap.search_emails(folder=new_created_empty_test_folder)

        half = math.floor(count / 2)
        one_part_of_emails = self.__class__._openmail.imap.get_emails(1, half)
        self.assertEqual(one_part_of_emails.total, half - 0)
        self.assertEqual([email.subject for email in one_part_of_emails.emails], random_subject_list[:half])

        other_part_of_emails = self.__class__._openmail.imap.get_emails(half + 1, count)
        self.assertEqual(other_part_of_emails.total, count - half)
        self.assertEqual([email.subject for email in other_part_of_emails.emails], random_subject_list[half:count])

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestFetchOperations`...")
        for folder_name in cls._created_test_folders:
            cls._openmail.imap.delete_folder(folder_name, True)
        if cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, ",".join(sorted(cls._sent_test_email_uids, key=int)))
        cls._openmail.disconnect()
