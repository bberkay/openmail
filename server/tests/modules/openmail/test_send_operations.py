import base64
import re
import unittest
import json
import copy

from src.modules.openmail import Openmail
from src.modules.openmail.types import Draft, Folder, SearchCriteria
from src.modules.openmail.parser import HTMLParser, MessageParser
from src.modules.openmail.encoder import FileBase64Encoder
from src.modules.openmail.converter import AttachmentConverter

from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator
from .utils.sample_file_generator import SampleDocumentGenerator, SampleImageGenerator, SampleVideoGenerator

class TestSendOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestSendOperations`...")
        cls.addClassCleanup(cls.cleanup)

        cls._openmail = Openmail()

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
        for key in ["sender", "receivers", "cc"]:
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
                                email_to_send_inline_attachment
                            )
                            email_to_send.body = email_to_send.body.replace(
                                email_to_send_inline_attachment,
                                f"data:{base64_data[1]};base64,{base64_data[3]}",
                                count=1
                            )
                    # Clean bodies
                    email_content.body = email_content.body.replace("base64, ", "base64,", count=1)
                    email_to_send.body = email_to_send.body.replace("base64, ", "base64,", count=1)
                    email_content.body = re.sub(r"\s+", "", email_content.body)
                    email_to_send.body = re.sub(r"\s+", "", email_to_send.body)

        self.assertMultiLineEqual(
            email_to_send.body.strip(),
            email_content.body.strip(),
        )

        # Attachments (strings or `Attachment` objects)
        if ("attachments" in email_to_send.keys() and email_to_send.attachments):
            if not "attachments" in email_content.keys() or not email_content.attachments:
                self.fail("Attachment(s) found in `email_to_send`, but no attachment detected in `email_content`.")

            self.assertCountEqual(
                [attachment.name for attachment in email_to_send.attachments],
                [attachment.name for attachment in email_content.attachments]
            )
            for attachment in email_to_send.attachments:
                found_attachment = self.__class__._openmail.imap.download_attachment(
                    Folder.Inbox,
                    email_content.uid,
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

    def test_send_basic_email(self):
        print("test_send_basic_email...")
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_basic_email"
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_multiple_recipients_email(self):
        print("test_send_multiple_recipients_email...")
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._receiver_emails[0:2],
            subject=NameGenerator.subject()[0],
            body="test_send_multiple_recipients_email",
            cc=self.__class__._receiver_emails[2],
            bcc=self.__class__._sender_email,
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_html_email(self):
        print("test_send_html_email...")
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
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
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_filepath_attachment(self):
        print("test_send_email_with_filepath_attachment...")
        sampleDocumentFiles = SampleDocumentGenerator().as_filepath(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_email_with_filepath_attachment",
            attachments=[
                AttachmentConverter.resolve_and_convert(sampleDocumentFiles[0]),
                AttachmentConverter.resolve_and_convert(sampleDocumentFiles[1]),
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_link_attachment(self):
        print("test_send_email_with_link_attachment...")
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_email_with_link_attachment",
            attachments=[
                AttachmentConverter.resolve_and_convert(sampleImageUrls[0]),
                AttachmentConverter.resolve_and_convert(sampleImageUrls[1]),
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_all_options_attachment(self):
        print("test_send_email_with_all_option_attachment...")
        sampleImageFiles = SampleImageGenerator().as_filepath(count=2, all_different=True)
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_email_with_all_options_attachment",
            attachments=[
                AttachmentConverter.resolve_and_convert(sampleImageFiles[0]),
                AttachmentConverter.resolve_and_convert(sampleImageUrls[0]),
                AttachmentConverter.resolve_and_convert(sampleImageFiles[1]),
                AttachmentConverter.resolve_and_convert(sampleImageUrls[1]),
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_inline_path_attachment(self):
        print("test_send_email_with_inline_path_attachment...")
        sampleImageFiles = SampleImageGenerator().as_filepath(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
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
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_inline_link_attachment(self):
        print("test_send_email_with_inline_link_attachment...")
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
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
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_inline_base64_attachment(self):
        print("test_send_email_with_inline_base64_attachment...")
        sampleImageFiles = SampleImageGenerator().as_base64(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
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
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_inline_all_options_attachment(self):
        print("test_send_email_with_inline_all_options_attachment...")
        sampleBase64Images = SampleImageGenerator().as_base64(count=2, all_different=True)
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        sampleImagePaths = SampleImageGenerator().as_filepath(count=2, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
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
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_both_attachment_and_inline_attachment(self):
        print("test_send_email_with_both_attachment_and_inline_attachment...")
        sampleImages = SampleImageGenerator().as_filepath(count=4, all_different=True)
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
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
                AttachmentConverter.resolve_and_convert(sampleImages[2]),
                AttachmentConverter.resolve_and_convert(sampleImages[3]),
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_duplicate_attachments(self):
        print("test_send_email_with_duplicate_attachments...")
        sampleImage1 = SampleImageGenerator().as_filepath()[0]
        sampleDocument2 = SampleDocumentGenerator().as_filepath()[0]
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
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
                AttachmentConverter.resolve_and_convert(sampleDocument2),
                AttachmentConverter.resolve_and_convert(sampleDocument2)
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_email_with_large_attachment(self):
        print("test_send_email_with_large_attachment...")
        sampleVideo = SampleVideoGenerator().as_filepath()[0]
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
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
                AttachmentConverter.resolve_and_convert(sampleVideo)
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_send_nonascii_name_attachment(self):
        print("test_send_nonascii_name_attachment...")
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_send_nonascii_name_attachment",
            attachments=[
                AttachmentConverter.resolve_and_convert(
                    SampleDocumentGenerator().as_filepath(include_nonascii=True)[0]
                )
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

    def test_reply_email(self):
        print("test_reply_email...")
        # Sent normal email
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_reply_email",
            attachments=[
                AttachmentConverter.resolve_and_convert(
                    SampleDocumentGenerator().as_filepath()[0]
                )
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

        # Find sent email to reply it.
        sent_email_content = self.__class__._openmail.imap.get_email_content(
            Folder.Inbox,
            uid
        )

        # Reply email
        reply_email_subject = NameGenerator.subject()[0]
        reply_email = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=reply_email_subject,
            body="test_reply_email",
        )
        status, _ = self.__class__._openmail.smtp.reply_email(
            sent_email_content.message_id,
            reply_email,
            sent_email_content.sender,
            sent_email_content.body,
            sent_email_content.date
        )
        self.assertTrue(status)

        # Find sent reply_email
        self.__class__._openmail.imap.search_emails(
            folder=Folder.Inbox,
            search=SearchCriteria(
                subject=reply_email_subject,
            )
        )

        mailbox = self.__class__._openmail.imap.get_emails()
        found_reply_email = mailbox.emails[0]

        self.__class__._sent_test_email_uids.append(found_reply_email.uid)

        # Check the reply if it has correct structure.
        self.assertTrue(found_reply_email.subject.startswith("Re: "))
        self.assertEqual(found_reply_email.in_reply_to, sent_email_content.message_id)
        assert found_reply_email.references is not None
        self.assertIn(sent_email_content.message_id, found_reply_email.references)

    def test_forward_email(self):
        print("test_forward_email...")
        # Sent normal email
        email_to_send = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=NameGenerator.subject()[0],
            body="test_forward_email",
            attachments=[
                AttachmentConverter.resolve_and_convert(
                    SampleDocumentGenerator().as_filepath()[0]
                )
            ],
        )
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            copy.copy(email_to_send)
        )
        self.__class__._sent_test_email_uids.append(uid)
        self.is_sent_email_valid(email_to_send, uid)

        # Find sent email to forward it.
        sent_email_content = self.__class__._openmail.imap.get_email_content(
            Folder.Inbox,
            uid
        )

        # Forward email
        forward_email_subject = NameGenerator.subject()[0]
        forward_email = Draft(
            sender=self.__class__._sender_email,
            receivers=self.__class__._sender_email,
            subject=forward_email_subject,
            body="forward_email_subject",
        )
        status, _ = self.__class__._openmail.smtp.forward_email(
            sent_email_content.message_id,
            forward_email,
            sent_email_content.sender,
            sent_email_content.receivers,
            sent_email_content.subject,
            sent_email_content.body,
            sent_email_content.date
        )
        self.assertTrue(status)

        # Find sent forward_email
        status, message = self.__class__._openmail.imap.search_emails(
            folder=Folder.Inbox,
            search=SearchCriteria(
                subject=forward_email_subject,
            )
        )
        self.assertTrue(status)

        mailbox = self.__class__._openmail.imap.get_emails()
        found_reply_email = mailbox.emails[0]

        self.__class__._sent_test_email_uids.append(found_reply_email.uid)

        # Check the forward if it has correct structure.
        self.assertTrue(found_reply_email.subject.startswith("Fwd: "))
        self.assertEqual(found_reply_email.in_reply_to, sent_email_content.message_id)
        assert found_reply_email.references is not None
        self.assertIn(sent_email_content.message_id, found_reply_email.references)

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestSendOperations`...")
        if cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, ",".join(sorted(cls._sent_test_email_uids, key=int)))
        cls._openmail.disconnect()
