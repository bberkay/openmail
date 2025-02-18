import time
from typing import cast
import unittest
import json
import threading

from openmail import OpenMail
from openmail.imap import Folder
from openmail.types import Draft
from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator

class TestIdleOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestIdleOperations`...")
        cls.addClassCleanup(cls.cleanup)

        cls._openmail = OpenMail()
        with open("./credentials.json") as credentials:
            cls._credentials = json.load(credentials)

        cls._email = cls._credentials[0]["email"]
        cls._openmail.connect(cls._email, cls._credentials[0]["password"])
        print(f"Connected to {cls._email}...")

        cls._sent_test_email_uids = []

    def test_idle_and_done(self):
        print("test_idle_and_done...")
        self.__class__._openmail.imap.idle()
        time.sleep(5)
        self.__class__._openmail.imap.done()

    def test_idle_lifecycle(self):
        print("test_idle_lifecycle...")
        for _ in range(0, 3):
            self.__class__._openmail.imap.idle()
            time.sleep(5)
            self.__class__._openmail.imap.done()
            time.sleep(2)

    def test_reconnection(self):
        print("test_reconnection...")
        self.__class__._openmail.imap.idle()
        print("Idle mode activated before waiting...")
        time.sleep(60 * 30)
        try:
            result = self.__class__._openmail.imap.get_folders()
            self.assertGreaterEqual(len(result), 1)
        except Exception as e:
            print("Error while fetching folders: ", e)
            print("Checking connection...")
            try:
                if self.__class__._openmail.imap.is_logged_out():
                    print(f"IMAPManager logged out from {self.__class__._email}")
                else:
                    print(f"IMAPManager seems stil logged in to {self.__class__._email}, going to try to disconnect...")
                    status, message = self.__class__._openmail.disconnect()
                    if not status: self.fail(message)
            except Exception as e:
                print("Error while checking connection: ", e)
            finally:
                print("Reconnecting...")
                try:
                    status, message = self.__class__._openmail.connect(
                        self.__class__._email,
                        self.__class__._credentials[0]["password"]
                    )
                    if not status: self.fail(message)

                    time.sleep(1)
                    self.__class__._openmail.imap.idle()
                    time.sleep(5)
                    result = self.__class__._openmail.imap.get_folders()
                    self.assertGreaterEqual(len(result), 1)
                except Exception as e:
                    self.fail("Error while reconnecting: " + str(e))

    def test_get_folders_in_idle_mode(self):
        print("test_get_folders_in_idle_mode...")
        self.__class__._openmail.imap.idle()
        time.sleep(3)
        result = self.__class__._openmail.imap.get_folders()
        self.assertGreaterEqual(len(result), 1)

    def test_get_emails_in_idle_mode(self):
        print("test_get_emails_in_idle_mode...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
        self.__class__._sent_test_email_uids.append(uid)
        self.__class__._openmail.imap.idle()
        time.sleep(3)
        self.__class__._openmail.imap.search_emails()
        time.sleep(3)
        result = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(result.emails), 1)

    def test_new_emails_in_idle_mode(self):
        print("test_new_emails_in_idle_mode...")
        self.__class__._openmail.imap.idle()
        time.sleep(3)

        new_message_received = threading.Event()

        def wait_for_new_email():
            remanining_time = 100
            while remanining_time > 0:
                time.sleep(1)
                if self.__class__._openmail.imap.any_new_email():
                    new_message_received.set()
                    break
                remanining_time -= 1

        wait_new_message_thread = threading.Thread(target=wait_for_new_email)
        wait_new_message_thread.start()

        # Sender
        sender = OpenMail()
        sender_email = self.__class__._credentials[2]["email"]
        sender.connect(sender_email, self.__class__._credentials[2]["password"])
        print(f"Connecting to {sender_email}")
        subject = cast(str, NameGenerator.subject()[0])
        sender.smtp.send_email(sender_email, Draft(
            receiver=self.__class__._email,
            subject=subject,
            body=NameGenerator.body()[0]
        ))
        sender.disconnect()
        print(f"{sender_email} sent {subject}")

        # Wait sent message
        while not new_message_received.is_set():
            print("Waiting for new message...")
            time.sleep(1)

        wait_new_message_thread.join()
        new_message_received.clear()
        emails = self.__class__._openmail.imap.get_recent_emails()
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0].sender, sender_email)
        self.assertEqual(emails[0].subject, subject)

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestIdleOperations`...")
        if cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, ",".join(cls._sent_test_email_uids))
        cls._openmail.disconnect()
