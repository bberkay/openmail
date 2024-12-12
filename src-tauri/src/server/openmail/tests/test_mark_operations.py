from openmail.imap import IMAPManager, Mark, Folder
from openmail.types import Mailbox
import time
import unittest

class TestMarkOperations(unittest.TestCase):

    def setUp(self, *args):
        self.imap = IMAPManager("testforprojects42webio@gmail.com", "udctmeicdwcbsknj")

    def test_flagged_operation(self):
        print("test_flagged_operation...")

        status, message = self.imap.search_emails()
        if not status:
            self.fail("Failed to search emails with status: ", status, " and message: ", message)

        flagged_uid = None
        mailbox = self.imap.get_emails()
        if len(mailbox.emails) == 0:
            self.fail("Mailbox is empty, failed to test flagged operation")

        for email in mailbox.emails:
            if Mark.Flagged not in email.flags:
                flagged_uid = email.uid
                print("flagged_uid: ", flagged_uid, " subject: ", email.subject)
                status, message = self.imap.mark_email(Mark.Flagged, flagged_uid)
                if status:
                    return self.assertTrue(True)
                else:
                    return self.fail("Failed to flag email with uid: ", flagged_uid, " with status: ", status, " and message: ", message)

        self.fail("End of `test_flagged_operation`, could not reached to the success condition")

    def test_unflagged_operation(self):
        print("test_unflagged_operation...")

        status, messsage = self.imap.search_emails(folder=Folder.Flagged)
        if not status:
            self.fail("Failed to search emails with status: ", status, " and message: ", messsage)

        unflagged_uid = None
        mailbox = self.imap.get_emails()
        if len(mailbox.emails) == 0:
            self.fail("Mailbox is empty, failed to test unflagged operation")

        for email in mailbox.emails:
            if Mark.Flagged in email.flags:
                unflagged_uid = email.uid
                print("unflagged_uid: ", unflagged_uid, " subject: ", email.subject)
                status, message = self.imap.unmark_email(Mark.Flagged, unflagged_uid, folder=Folder.Flagged)
                if status:
                    return self.assertTrue(True)
                else:
                    return self.fail("Failed to unflag email with uid: ", unflagged_uid, " with status: ", status, " and message: ", message)

        self.fail("End of `test_unflagged_operation`, could not reached to the success condition")

    def tearDown(self, *args):
        self.imap.logout()
