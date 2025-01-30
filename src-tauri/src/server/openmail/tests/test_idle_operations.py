import re
import time
import unittest
import json

from openmail import OpenMail
from openmail.imap import Folder
from .utils.dummy_operator import DummyOperator

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
        #uid = DummyOperator.send_test_email_to_self_and_get_uid(cls._openmail, cls._email)
        #cls._sent_test_email_uids.append(uid)

    def test_idle_and_done(self):
        print("test_idle_and_done...")
        self.__class__._openmail.imap.idle()
        time.sleep(10)
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
        print("idle mode activated before waiting...")
        time.sleep(60 * 30)
        try:
            result = self.__class__._openmail.imap.get_folders()
            print("get folders after a long time: ",result)
            self.assertGreaterEqual(len(result), 1)
        except Exception as e:
            print("Exception raised: ", e)
            print("reconnecting...")
            try:
                self.__class__._openmail.disconnect()
            except Exception as e:
                print("Error while disconnecting...: ", e)
            finally:
                try:
                    result2 = self.__class__._openmail.connect(
                        self.__class__._email,
                        self.__class__._credentials[0]["password"]
                    )
                    print("connect result2: ", result2)
                    if result2[0]:
                        time.sleep(3)
                        self.__class__._openmail.idle()
                        time.sleep(5)
                        result4 = self.__class__._openmail.imap.get_folders()
                        print("get folder test4: ", result4)
                        print("WORKING")
                        self.assertGreaterEqual(len(result4), 1)
                    else:
                        print("CONNECT FAILED it seems")
                        self.fail("CONNECT COMP FAILED")
                except Exception as t:
                    print("reconnecte connect t: ", t)
                    print("FAILED it seems")
                    self.fail("COMP FAILED")

        print("finished")

    def test_get_folders_in_idle_mode(self):
        print("test_get_folders_in_idle_mode...")
        self.__class__._openmail.imap.idle()
        time.sleep(5)
        result = self.__class__._openmail.imap.get_folders()
        self.assertGreaterEqual(len(result), 1)

    def test_get_emails_in_idle_mode(self):
        print("test_get_emails_in_idle_mode...")
        self.__class__._openmail.imap.idle()
        time.sleep(5)
        self.__class__._openmail.imap.search_emails()
        time.sleep(3)
        result = self.__class__._openmail.imap.get_emails()
        self.assertGreaterEqual(len(result.emails), 1)

    def test_new_emails_in_idle_mode(self):
        pass

    @classmethod
    def cleanup(cls):
        print("Cleaning up test `TestIdleOperations`...")
        if cls._sent_test_email_uids:
            cls._openmail.imap.delete_email(Folder.Inbox, ",".join(cls._sent_test_email_uids))
        cls._openmail.disconnect()
