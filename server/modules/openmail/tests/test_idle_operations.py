import time
from typing import Callable, cast
import unittest
import json
import threading

from modules.openmail import Openmail
from modules.openmail.imap import IDLE_ACTIVATION_INTERVAL, IDLE_TIMEOUT, Folder
from modules.openmail.types import Draft
from .utils.dummy_operator import DummyOperator
from .utils.name_generator import NameGenerator

class TestIdleOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up test `TestIdleOperations`...")
        cls.addClassCleanup(cls.cleanup)

        cls._openmail = Openmail()
        with open("./credentials.json") as credentials:
            cls._credentials = json.load(credentials)

        cls._email = cls._credentials[0]["email"]
        cls._openmail.connect(
            cls._email,
            cls._credentials[0]["password"],
            imap_enable_idle_optimization=False
        )
        print(f"Connected to {cls._email}...")

        cls._sent_test_email_uids = []

    @staticmethod
    def enable_idle_optimization(optimized_idle_test: Callable):
        def wrapper(self, *args, **kwargs):
            if not self.__class__._openmail.imap.is_idle_optimization_enabled():
                print(f"Idle must be enabled for {optimized_idle_test.__name__} but it is not. Logging out to enable optimization...")
                self.__class__._openmail.disconnect()
                self.__class__._openmail.connect(
                    self.__class__._email,
                    self.__class__._credentials[0]["password"],
                    imap_enable_idle_optimization=True
                )
                print(f"Idle optimization is now enabled. Running {optimized_idle_test.__name__}...")
            return optimized_idle_test(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def disable_idle_optimization(standard_idle_test: Callable):
        def wrapper(self, *args, **kwargs):
            if self.__class__._openmail.imap.is_idle_optimization_enabled():
                print(f"Idle must be disabled for {standard_idle_test.__name__}, but it is not. Logging out to disable optimization...")
                self.__class__._openmail.imap.logout()
                self.__class__._openmail.connect(
                    self.__class__._email,
                    self.__class__._credentials[0]["password"],
                    imap_enable_idle_optimization=False
                )
                print(f"Idle optimization is now disabled. Running {standard_idle_test.__name__}...")
            return standard_idle_test(self, *args, **kwargs)

        return wrapper

    @disable_idle_optimization
    def test_idle_and_done(self):
        print("test_idle_and_done...")
        self.__class__._openmail.imap.idle()
        time.sleep(5)
        self.__class__._openmail.imap.done()

    @disable_idle_optimization
    def test_idle_lifecycle(self):
        print("test_idle_lifecycle...")
        for _ in range(0, 3):
            self.__class__._openmail.imap.idle()
            time.sleep(5)
            self.__class__._openmail.imap.done()
            time.sleep(2)

    @disable_idle_optimization
    def test_is_idle(self):
        print("test_is_idle...")
        self.assertFalse(self.__class__._openmail.imap.is_idle())
        self.__class__._openmail.imap.idle()
        time.sleep(5)
        self.assertTrue(self.__class__._openmail.imap.is_idle())
        time.sleep(1)
        self.__class__._openmail.imap.done()
        time.sleep(1)
        self.assertFalse(self.__class__._openmail.imap.is_idle())

    @disable_idle_optimization
    def test_get_folders_in_idle_mode(self):
        print("test_get_folders_in_idle_mode...")
        self.__class__._openmail.imap.idle()
        time.sleep(3)
        result = self.__class__._openmail.imap.get_folders()
        self.assertGreaterEqual(len(result), 1)

    @disable_idle_optimization
    def test_get_emails_in_idle_mode(self):
        print("test_get_emails_in_idle_mode...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
        self.__class__._sent_test_email_uids.append(uid)
        self.__class__._openmail.imap.idle()
        time.sleep(3)
        self.__class__._openmail.imap.search_emails()
        result = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(result.emails), 1)

    @disable_idle_optimization
    def test_get_folders_in_idle_mode_without_waiting_for_idle_mode(self):
        print("test_get_folders_in_idle_mode_without_waiting_for_idle_mode...")
        self.__class__._openmail.imap.idle()
        result = self.__class__._openmail.imap.get_folders()
        self.assertGreaterEqual(len(result), 1)

    @disable_idle_optimization
    def test_get_emails_in_idle_mode_without_waiting_for_idle_mode(self):
        print("test_get_emails_in_idle_mode_without_waiting_for_idle_mode...")
        uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
        self.__class__._sent_test_email_uids.append(uid)
        self.__class__._openmail.imap.idle()
        self.__class__._openmail.imap.search_emails()
        result = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(result.emails), 1)

    @disable_idle_optimization
    def test_idle_timeout(self):
        print("test_idle_timeout...")
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_TIMEOUT + (IDLE_TIMEOUT / 2))
        self.assertTrue(self.__class__._openmail.imap.is_idle())

    @disable_idle_optimization
    def test_idle_reconnection(self):
        print("test_reconnection...")
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_TIMEOUT + (IDLE_TIMEOUT / 2))
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
                    time.sleep(2)
                    result = self.__class__._openmail.imap.get_folders()
                    self.assertGreaterEqual(len(result), 1)
                except Exception as e:
                    self.fail("Error while reconnecting: " + str(e))

    @disable_idle_optimization
    def test_new_emails_in_idle_mode(self):
        print("test_new_emails_in_idle_mode...")
        self.__class__._openmail.imap.idle()
        time.sleep(3)

        new_message_received = threading.Event()

        def wait_for_new_email():
            while True:
                if self.__class__._openmail.imap.any_new_email():
                    new_message_received.set()
                    break
                time.sleep(1)

        wait_new_message_thread = threading.Thread(target=wait_for_new_email)
        wait_new_message_thread.start()

        # Sender
        sender = Openmail()
        sender_email = self.__class__._credentials[2]["email"]
        sender.connect(sender_email, self.__class__._credentials[2]["password"])
        print(f"Connecting to {sender_email}")
        subject = cast(str, NameGenerator.subject()[0])
        sender.smtp.send_email(Draft(
            sender=sender_email,
            receivers=self.__class__._email,
            subject=subject,
            body=NameGenerator.body()[0]
        ))
        sender.disconnect()
        print(f"{sender_email} sent {subject}")

        # Wait sent message
        timeout = 100
        while timeout > 0:
            if new_message_received.is_set():
                break
            print("Waiting for new message...")
            timeout -= 1
            time.sleep(1)

        wait_new_message_thread.join(timeout=5)
        if not new_message_received.is_set():
            self.fail(f"No message received in given time({timeout}s).")

        new_message_received.clear()
        emails = self.__class__._openmail.imap.get_recent_emails()
        self.assertGreaterEqual(len(emails), 1)
        self.assertEqual(emails[0].sender, sender_email)
        self.assertEqual(emails[0].subject, subject)

    @unittest.skipIf(IDLE_ACTIVATION_INTERVAL < 10, "IDLE_ACTIVATION_INTERVAL must be at least 10 for testing.")
    @enable_idle_optimization
    def test_idle_optimization(self):
        print("test_idle_optimization...")
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_ACTIVATION_INTERVAL / 2)
        old_activation_countdown = self.__class__._openmail.imap._idle_activation_countdown
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_ACTIVATION_INTERVAL / 4)
        reset_activation_countdown = self.__class__._openmail.imap._idle_activation_countdown
        self.assertGreater(reset_activation_countdown, old_activation_countdown)
        time.sleep(IDLE_ACTIVATION_INTERVAL + 10)
        self.__class__._openmail.imap.done()

    @unittest.skipIf(IDLE_ACTIVATION_INTERVAL < 10, "IDLE_ACTIVATION_INTERVAL must be at least 10 for testing.")
    @enable_idle_optimization
    def test_is_idle_when_idle_optimization_is_true(self):
        print("test_is_idle_while_not_in_optimized_idle_mode...")
        self.assertFalse(self.__class__._openmail.imap.is_idle())
        self.assertFalse(self.__class__._openmail.imap.is_idle_activation_countdown_continue())
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_ACTIVATION_INTERVAL / 2)
        self.assertTrue(self.__class__._openmail.imap.is_idle_activation_countdown_continue())
        self.assertFalse(self.__class__._openmail.imap.is_idle())
        time.sleep((IDLE_ACTIVATION_INTERVAL / 2) + 3) # wait 3 seconds after activation countdown finished.
        self.assertFalse(self.__class__._openmail.imap.is_idle_activation_countdown_continue())
        self.assertTrue(self.__class__._openmail.imap.is_idle())
        self.__class__._openmail.imap.done()
        time.sleep(1)
        self.assertFalse(self.__class__._openmail.imap.is_idle_activation_countdown_continue())
        self.assertFalse(self.__class__._openmail.imap.is_idle())

    @unittest.skipIf(IDLE_ACTIVATION_INTERVAL < 10, "IDLE_ACTIVATION_INTERVAL must be at least 10 for testing.")
    @enable_idle_optimization
    def test_optimized_idle_lifecycle(self):
        print("test_optimized_idle_lifecycle...")
        for _ in range(0, 3):
            self.__class__._openmail.imap.idle()
            time.sleep(IDLE_ACTIVATION_INTERVAL / 2)
            old_activation_countdown = self.__class__._openmail.imap._idle_activation_countdown
            self.__class__._openmail.imap.idle()
            time.sleep(IDLE_ACTIVATION_INTERVAL / 4)
            reset_activation_countdown = self.__class__._openmail.imap._idle_activation_countdown
            self.assertGreater(reset_activation_countdown, old_activation_countdown)
            time.sleep(IDLE_ACTIVATION_INTERVAL + 10)
            self.__class__._openmail.imap.done()

    @enable_idle_optimization
    def test_get_folders_in_optimized_idle_mode(self):
        print("test_get_folders_in_optimized_idle...")
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_ACTIVATION_INTERVAL + 10)
        result = self.__class__._openmail.imap.get_folders()
        self.assertGreaterEqual(len(result), 1)

    @enable_idle_optimization
    def test_get_emails_in_optimized_idle_mode(self):
        print("test_get_emails_in_optimized_idle...")
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_ACTIVATION_INTERVAL + 10)
        self.__class__._openmail.imap.search_emails()
        result = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(result.emails), 1)

    @enable_idle_optimization
    def test_get_folders_in_optimized_idle_mode_without_waiting_for_idle_mode(self):
        print("test_get_folders_in_optimized_idle_without_waiting_for_idle_mode...")
        self.__class__._openmail.imap.idle()
        result = self.__class__._openmail.imap.get_folders()
        self.assertGreaterEqual(len(result), 1)

    @enable_idle_optimization
    def test_get_emails_in_optimized_idle_mode_without_waiting_for_idle_mode(self):
        print("test_get_emails_in_optimized_idle_without_waiting_for_idle_mode...")
        self.__class__._openmail.imap.idle()
        self.__class__._openmail.imap.search_emails()
        result = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(result.emails), 1)

    @enable_idle_optimization
    def test_optimized_idle_timeout(self):
        print("test_optimized_idle_timeout...")
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_ACTIVATION_INTERVAL + IDLE_TIMEOUT + IDLE_ACTIVATION_INTERVAL + (IDLE_TIMEOUT / 2))
        self.assertTrue(self.__class__._openmail.imap.is_idle())

    @enable_idle_optimization
    def test_optimized_idle_reconnection(self):
        print("test_optimized_idle_reconnection...")
        self.__class__._openmail.imap.idle()
        time.sleep(IDLE_TIMEOUT + (IDLE_TIMEOUT / 2))
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
                        self.__class__._credentials[0]["password"],
                        imap_enable_idle_optimization=True
                    )
                    if not status: self.fail(message)
                    time.sleep(1)
                    self.__class__._openmail.imap.idle()
                    time.sleep(2)
                    result = self.__class__._openmail.imap.get_folders()
                    self.assertGreaterEqual(len(result), 1)
                except Exception as e:
                    self.fail("Error while reconnecting: " + str(e))

    @enable_idle_optimization
    def test_new_emails_in_optimized_idle_mode(self):
        print("test_new_emails_in_optimized_idle_mode...")
        self.__class__._openmail.imap.idle()
        time.sleep(3)

        new_message_received = threading.Event()

        def wait_for_new_email():
            while True:
                if self.__class__._openmail.imap.any_new_email():
                    new_message_received.set()
                    break
                time.sleep(1)

        wait_new_message_thread = threading.Thread(target=wait_for_new_email)
        wait_new_message_thread.start()

        """
        An important problem about idle optimization is when
        new messages arrive while idle still waiting for activation,
        their EXISTS messages is NOT going to be handled since IDLE
        mode won't be enabled. So we will wait IDLE_ACTIVATION time
        before sending test email but in real product, new messages
        should be listening in standard idle mode and most highly
        in their own threads which will necessitate new imap connection.
        """
        time.sleep(IDLE_ACTIVATION_INTERVAL + (IDLE_TIMEOUT / 2))

        # Sender
        sender = Openmail()
        sender_email = self.__class__._credentials[2]["email"]
        sender.connect(sender_email, self.__class__._credentials[2]["password"])
        print(f"Connecting to {sender_email}")
        subject = cast(str, NameGenerator.subject()[0])
        sender.smtp.send_email(Draft(
            sender=sender_email,
            receivers=self.__class__._email,
            subject=subject,
            body=NameGenerator.body()[0]
        ))
        sender.disconnect()
        print(f"{sender_email} sent {subject}")

        # Wait sent message
        timeout = 100
        while timeout > 0:
            if new_message_received.is_set():
                break
            print("Waiting for new message...")
            timeout -= 1
            time.sleep(1)

        wait_new_message_thread.join(timeout=5)
        if not new_message_received.is_set():
            self.fail(f"No message received in given time({timeout}s).")

        new_message_received.clear()
        emails = self.__class__._openmail.imap.get_recent_emails()
        self.assertGreaterEqual(len(emails), 1)
        self.assertEqual(emails[0].sender, sender_email)
        self.assertEqual(emails[0].subject, subject)

    def test_is_optimized_idle_mode_is_really_optimized(self):
        print("test_is_optimized_idle_mode_is_really_optimized...")

        @TestIdleOperations.disable_idle_optimization
        def measure_task_duration_in_idle_mode(self):
            print("Standard IDLE mode testing...")
            standard_start_time = time.time()
            self.__class__._openmail.imap.idle()
            result = self.__class__._openmail.imap.get_folders()
            self.assertGreaterEqual(len(result), 1)
            uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
            self.__class__._sent_test_email_uids.append(uid)
            self.__class__._openmail.imap.idle()
            self.__class__._openmail.imap.search_emails()
            result = self.__class__._openmail.imap.get_emails()
            self.assertGreaterEqual(len(result.emails), 1)
            standard_end_time = time.time()
            standard_duration = standard_end_time - standard_start_time
            return standard_duration

        @TestIdleOperations.enable_idle_optimization
        def measure_task_duration_in_optimized_idle_mode(self):
            print("Optimized IDLE mode testing...")
            optimized_start_time = time.time()
            self.__class__._openmail.imap.idle()
            result = self.__class__._openmail.imap.get_folders()
            self.assertGreaterEqual(len(result), 1)
            uid = DummyOperator.send_test_email_to_self_and_get_uid(self.__class__._openmail, self.__class__._email)
            self.__class__._sent_test_email_uids.append(uid)
            self.__class__._openmail.imap.idle()
            self.__class__._openmail.imap.search_emails()
            result = self.__class__._openmail.imap.get_emails()
            self.assertGreaterEqual(len(result.emails), 1)
            optimized_end_time = time.time()
            optimized_duration = optimized_end_time - optimized_start_time
            return optimized_duration

        standard_duration = measure_task_duration_in_idle_mode(self)
        optimized_duration = measure_task_duration_in_optimized_idle_mode(self)
        print(f"Standard idle duration: {standard_duration:.4f} seconds")
        print(f"Optimized idle duration: {optimized_duration:.4f} seconds")
        self.assertLess(optimized_duration, standard_duration)

        speedup_percentage = ((standard_duration - optimized_duration) / standard_duration) * 100
        print(f"Optimized idle is {speedup_percentage:.2f}% faster")

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestIdleOperations`...")
        if cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, ",".join(cls._sent_test_email_uids))
        cls._openmail.disconnect()
