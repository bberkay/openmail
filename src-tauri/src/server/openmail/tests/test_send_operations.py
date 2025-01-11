import unittest
import json

from openmail import OpenMail
from openmail.types import Attachment, EmailToSend, Folder
from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator
from .utils.sample_file_generator import SampleDocumentGenerator, SampleImageGenerator, SampleVideoGenerator

class TestSendOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestSendOperations`...")
        cls._openmail = OpenMail()

        with open("openmail/tests/credentials.json") as credentials:
            credentials = json.load(credentials)

        cls._email = credentials[0]["email"]
        cls._openmail.connect(cls._email, credentials[0]["password"])

        cls._sent_test_email_uids = []

    def test_send_basic_email(self):
        print("test_send_basic_email...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
                body="test_send_basic_email",
                cc=self.__class__._email,
                bcc=self.__class__._email,
            )
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_html_email(self):
        print("test_send_html_email...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
                body=f'''
                <html>
                    <head></head>
                    <body>
                        <hr/>
                        <i>test_send_html_email</i>
                        <hr/>
                    </body>
                </html>
                ''',
            )
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_filepath_attachment(self):
        print("test_send_email_with_filepath_attachment...")
        sampleDocumentFiles = SampleDocumentGenerator().as_filepath(count=2, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
                body="test_send_email_with_filepath_attachment",
                attachments=[
                    sampleDocumentFiles[0],
                    Attachment(path=sampleDocumentFiles[1]),
                ],
            )
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_link_attachment(self):
        print("test_send_email_with_link_attachment...")
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
                body="test_send_email_with_link_attachment",
                attachments=[
                    sampleImageUrls[0],
                    Attachment(path=sampleImageUrls[1]),
                ],
            )
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_all_options_attachment(self):
        print("test_send_email_with_all_option_attachment...")
        sampleImageFiles = SampleImageGenerator().as_filepath(count=2, all_different=True)
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
                body="test_send_email_with_all_options_attachment",
                attachments=[
                    sampleImageFiles[0],
                    sampleImageUrls[0],
                    Attachment(path=sampleImageFiles[1]),
                    Attachment(path=sampleImageUrls[1]),
                ],
            )
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_inline_path_attachment(self):
        print("test_send_email_with_inline_path_attachment...")
        sampleImageFiles = SampleImageGenerator().as_filepath(count=2, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
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
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_inline_link_attachment(self):
        print("test_send_email_with_inline_link_attachment...")
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
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
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_inline_base64_attachment(self):
        print("test_send_email_with_inline_base64_attachment...")
        sampleImageFiles = SampleImageGenerator().as_base64(count=2, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
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
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_inline_all_options_attachment(self):
        print("test_send_email_with_inline_all_options_attachment...")
        sampleBase64Images = SampleImageGenerator().as_base64(count=2, all_different=True)
        sampleImageUrls = SampleImageGenerator().as_url(count=2, all_different=True)
        sampleImagePaths = SampleImageGenerator().as_filepath(count=2, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
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
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_attachment_and_inline_attachment(self):
        print("test_send_email_with_attachment_and_inline_attachment...")
        sampleImages = SampleImageGenerator().as_filepath(count=4, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
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
                    sampleImages[2],
                    Attachment(path=sampleImages[3]),
                ],
            )
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_duplicate_attachments(self):
        print("test_send_email_with_duplicate_attachments...")
        sampleDocument1 = SampleImageGenerator().as_filepath(count=1, all_different=True)
        sampleDocument2 = SampleDocumentGenerator().as_filepath(count=1, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
                body=f'''
                <html>
                    <head></head>
                    <body>
                        <hr/>
                        <i>test_send_email_with_duplicate_attachments</i>
                        <br>
                        <img src="{sampleDocument1}"/>
                        <img src="{sampleDocument1}"/>
                        <hr/>
                    </body>
                </html>
                ''',
                attachments=[
                    sampleDocument2,
                    Attachment(path=sampleDocument2)
                ],
            )
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    def test_send_email_with_large_attachment(self):
        print("test_send_email_with_large_attachment...")
        sampleVideo = SampleVideoGenerator().as_filepath(count=1, all_different=True)
        uid = DummyOperator.send_test_email_to_self_and_get_uid(
            self.__class__._openmail,
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
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
                    Attachment(path=sampleVideo)
                ],
            )
        )
        self.assertTrue(self.__class__._openmail.imap.is_email_exists(Folder.Inbox, uid))
        self._sent_test_email_uids.append(uid)

    """def test_reply_email(self):
        print("test_reply_email...")
        status, _ = self.__class__._smtp.reply_email(
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=NameGenerator.random_subject_with_uuid(),
                body=NameGenerator.random_body_with_uuid(),
            )
        )
        self.assertTrue(status)

    def test_forward_email(self):
        print("test_forward_email...")
        status, _ = self.__class__._smtp.forward_email(
            EmailToSend(
                sender=self.__class__._email,
                receiver=self.__class__._email,
                subject=generate_random_subject_with_uuid(),
                body=NameGenerator.random_body_with_uuid(),
            )
        )
        self.assertTrue(status)"""

    @classmethod
    def tearDownClass(cls):
        for uid in cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, uid)
        cls._openmail.disconnect()
