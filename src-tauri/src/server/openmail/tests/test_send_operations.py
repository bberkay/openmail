import os
import re
import unittest
import json
import copy
from typing import cast

from openmail import OpenMail
from openmail.types import Attachment, Draft, Email, Folder
from openmail.parser import HTMLParser, MessageParser
from openmail.encoder import FileBase64Encoder
from openmail.converter import AttachmentConverter

from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator
from .utils.sample_file_generator import SampleDocumentGenerator, SampleImageGenerator, SampleVideoGenerator

class TestSendOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestSendOperations`...")
        cls.addClassCleanup(cls.cleanup)

        cls._openmail = OpenMail()

        with open("./credentials.json") as credentials:
            credentials = json.load(credentials)

        if len(credentials) < 4:
            raise ValueError("At least 4 credentials are required.")

        cls._sender_email = credentials[0]["email"]
        cls._receiver_emails = [credential["email"] for credential in credentials]
        cls._openmail.connect(cls._sender_email, credentials[0]["password"])

        cls._sent_test_email_uids = []

    def is_sent_email_valid(self, email_to_send: Draft, uid: str):
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        email_content = self.__class__._openmail.imap.get_email_content(Folder.Inbox, uid)

        # Recipients
        for key in ["sender", "receiver", "cc", "bcc"]:
            self.assertCountEqual(
                [email.strip() for email in email_content[key].split(",")],
                (
                    [email.strip() for email in email_to_send[key].split(",")]
                    if isinstance(email_to_send[key], str)
                    else email_to_send[key]
                )
            )

        # Subject
        self.assertEqual(
            email_content.subject,
            email_to_send.subject
        )

        # Body (and inline attachments if body is html)
        if HTMLParser.is_html(email_to_send.body):
            # Replace cids in `email_to_send` with base64 data to compare
            # with `email_content`
            inline_srcs = MessageParser.get_inline_attachment_sources(email_to_send.body)
            if inline_srcs:
                email_to_send_inline_attachments = [match[1] for match in inline_srcs]
                if email_to_send_inline_attachments:
                    for email_to_send_inline_attachment in email_to_send_inline_attachments:
                        if not email_to_send_inline_attachment.startswith("data:"):
                            base64_data = FileBase64Encoder.read_file(
                                cast(str, AttachmentConverter.resolve_and_convert(
                                    email_to_send_inline_attachment
                                ).path)
                            )
                            email_to_send.body = email_to_send.body.replace(
                                email_to_send_inline_attachment,
                                f"data:{base64_data[1]};base64,{base64_data[3]}",
                                count=1
                            )
                    email_content.body = email_content.body.replace("base64, ", "base64,", count=1)
                    email_to_send.body = email_to_send.body.replace("\r", "").replace("\n", "")
                    email_content.body = email_content.body.replace("\r", "").replace("\n", "")

        self.assertEqual(
            email_to_send.body,
            email_content.body,
        )

        # Attachments (strings or `Attachment` objects)
        if ("attachments" in email_to_send.keys() and email_to_send.attachments):
            if not "attachments" in email_content.keys() or not email_content.attachments:
                self.fail("There is no attachment in `email_content`")

            self.assertCountEqual(
                [attachment.name for attachment in email_to_send.attachments],
                [attachment.name for attachment in email_content.attachments]
            )
            for attachment in email_content.attachments:
                found_attachment = self.__class__._openmail.imap.download_attachment(
                    Folder.Inbox,
                    email_content.uid,
                    attachment.name,
                    attachment.cid or ""
                )

                target_attachment = None
                for attachment in email_to_send.attachments:
                    if attachment.name == found_attachment.name:
                        target_attachment = attachment

                assert target_attachment is not None
                assert found_attachment is not None

                for field in set(target_attachment.keys() + found_attachment.keys()):
                    self.assertEqual(
                        target_attachment[field],
                        found_attachment[field]
                    )

    def test_send_basic_email(self):
        print("test_send_basic_email...")
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_basic_email"
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_multiple_recipients_email(self):
        print("test_send_multiple_recipients_email...")
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._receiver_emails[0:2],
            subject=NameGenerator.subject()[0],
            body="test_send_multiple_recipients_email",
            cc=self.__class__._receiver_emails[2],
            bcc=self.__class__._sender_email,
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_html_email(self):
        print("test_send_html_email...")
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    {NameGenerator.body()[0]}
                    <i>test_send_html_email</i>
                    <hr/>
                </body>
            </html>
            ''',
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_filepath_attachment(self):
        print("test_send_email_with_filepath_attachment...")
        sampleDocumentFiles = SampleDocumentGenerator().as_filepath(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_email_with_filepath_attachment",
            attachments=[
                Attachment.create(sampleDocumentFiles[0]),
                Attachment.create(sampleDocumentFiles[1]),
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_link_attachment(self):
        print("test_send_email_with_link_attachment...")
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_email_with_link_attachment",
            attachments=[
                Attachment.create(sampleImageUrls[0]),
                Attachment.create(sampleImageUrls[1]),
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_all_options_attachment(self):
        print("test_send_email_with_all_option_attachment...")
        sampleImageFiles = SampleImageGenerator().as_filepath(count=2, all_different=True)
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_email_with_all_options_attachment",
            attachments=[
                Attachment.create(sampleImageFiles[0]),
                Attachment.create(sampleImageUrls[0]),
                Attachment.create(sampleImageFiles[1]),
                Attachment.create(sampleImageUrls[1]),
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_inline_path_attachment(self):
        print("test_send_email_with_inline_path_attachment...")
        sampleImageFiles = SampleImageGenerator().as_filepath(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    <i>test_send_email_with_inline_path_attachment</i>
                    <br>
                    <img src="{sampleImageFiles[0]}"/>
                    <img src="{sampleImageFiles[1]}"/>
                    <hr/>
                </body>
            </html>
            '''
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_inline_link_attachment(self):
        print("test_send_email_with_inline_link_attachment...")
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    <i>test_send_email_with_inline_link_attachment</i>
                    <br>
                    <img src="{sampleImageUrls[0]}"/>
                    <img src="{sampleImageUrls[1]}"/>
                    <hr/>
                </body>
            </html>
            '''
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_inline_base64_attachment(self):
        print("test_send_email_with_inline_base64_attachment...")
        sampleImageFiles = SampleImageGenerator().as_base64(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    <i>test_send_email_with_inline_base64_attachment</i>
                    <br>
                    <img src="{sampleImageFiles[0]}"/>
                    <img src="{sampleImageFiles[1]}"/>
                    <hr/>
                </body>
            </html>
            '''
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_inline_all_options_attachment(self):
        print("test_send_email_with_inline_all_options_attachment...")
        sampleBase64Images = SampleImageGenerator().as_base64(count=2, all_different=True)
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        sampleImagePaths = SampleImageGenerator().as_filepath(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    <i>test_send_email_with_inline_all_options_attachment</i>
                    <br>
                    <img src="{sampleBase64Images[0]}"/>
                    <img src="{sampleBase64Images[1]}"/>
                    <img src="{sampleImageUrls[0]}"/>
                    <img src="{sampleImageUrls[1]}"/>
                    <img src="{sampleImagePaths[0]}"/>
                    <img src="{sampleImagePaths[1]}"/>
                    <hr/>
                </body>
            </html>
            '''
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_both_attachment_and_inline_attachment(self):
        print("test_send_email_with_both_attachment_and_inline_attachment...")
        sampleImages = SampleImageGenerator().as_filepath(count=4, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    <i>test_send_email_with_attachment_and_inline_attachment</i>
                    <br>
                    <img src="{sampleImages[0]}"/>
                    <img src="{sampleImages[1]}"/>
                    <hr/>
                </body>
            </html>
            ''',
            attachments=[
                Attachment.create(sampleImages[2]),
                Attachment.create(sampleImages[3]),
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_duplicate_attachments(self):
        print("test_send_email_with_duplicate_attachments...")
        sampleImage1 = SampleImageGenerator().as_filepath()[0]
        sampleDocument2 = SampleDocumentGenerator().as_filepath()[0]
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    <i>test_send_email_with_duplicate_attachments</i>
                    <br>
                    <img src="{sampleImage1}"/>
                    <img src="{sampleImage1}"/>
                    <hr/>
                </body>
            </html>
            ''',
            attachments=[
                Attachment.create(sampleDocument2),
                Attachment.create(sampleDocument2)
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_large_attachment(self):
        print("test_send_email_with_large_attachment...")
        sampleVideo = SampleVideoGenerator().as_filepath()[0]
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receiver=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body=f'''
            <html>
                <head></head>
                <body>
                    <hr/>
                    <i>test_send_email_with_large_attachment</i>
                    <hr/>
                </body>
            </html>
            ''',
            attachments=[
                Attachment.create(sampleVideo)
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    """def test_reply_email(self):
        print("test_reply_email...")
        status, _ = self.__class__._smtp.reply_email(
            Draft(
                sender=self.__class__._sender_email,
                receiver=self.__class__._sender_email,
                subject=NameGenerator.subject()[0],
                body=NameGenerator.body()[0],
            )
        )
        self.assertTrue(status)

    def test_forward_email(self):
        print("test_forward_email...")
        status, _ = self.__class__._smtp.forward_email(
            Draft(
                sender=self.__class__._sender_email,
                receiver=self.__class__._sender_email,
                subject=generate_random_subject_with_uuid(),
                body=NameGenerator.body()[0],
            )
        )
        self.assertTrue(status)"""

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestSendOperations`...")
        """for uid in cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, uid)"""
        cls._openmail.disconnect()
