import time

from openmail import OpenMail
from openmail.smtp import SMTPManagerException
from openmail.imap import IMAPManagerException
from openmail.types import DraftEmail, SearchCriteria, Folder
from openmail.tests.utils.name_generator import NameGenerator

class DummyOperator:
    """Dummy operator for testing purposes."""

    @staticmethod
    def create_test_folder_and_get_name(
        openmail: OpenMail,
        folder_name_suffix: str | None = None,
        create_parent: bool = False,
        parent_folder_name_suffix: str | None = None,
    ) -> str | tuple[str, str]:
        """
        Creates a test folder and returns its name.

        Args:
            openmail (OpenMail): An instance of the OpenMail class.
            folder_name_suffix (str, optional): The beginning of name of the folder to create.
            If not provided, a random name will be generated.
            create_parent (bool, optional): Whether to create a parent folder. Default is False.
            parent_folder_name_suffix (str, optional): The beginning of name of the parent folder
            to create. If not provided and create_parent is True, a random name will be generated.

        Returns:
            str: The name of the created folder.

        Example:
            >>> OpenMailDummyOperator.create_test_folder_and_get_name(openmail)
            'openmail-folder-test-uuid'
            >>> OpenMailDummyOperator.create_test_folder_and_get_name(openmail, create_parent=True)
            ('openmail-folder-test-uuid', 'openmail-folder-test-uuid') # (Child folder, Parent folder)
            >>> OpenMailDummyOperator.create_test_folder_and_get_name(
            ...     openmail,
            ...     create_parent=True,
            ...     parent_folder_name="already-exists-or-going-to-be-created"
            ... )
            ('openmail-folder-test-uuid', 'already-exists-or-going-to-be-created--uid') # (Child folder, parent_folder_name)
        """
        print("Creating test folder...")
        if not folder_name_suffix:
            folder_name_suffix = ""
        if not parent_folder_name_suffix:
            parent_folder_name_suffix = ""

        folder_name = folder_name_suffix + NameGenerator.folder_name()

        parent_folder_name = None
        if create_parent:
            parent_folder_name = parent_folder_name_suffix + NameGenerator.folder_name()

        openmail.imap.create_folder(folder_name, parent_folder_name)
        return (folder_name, parent_folder_name) if parent_folder_name else folder_name

    @staticmethod
    def send_test_email_to_self_and_get_uid(
        openmail: OpenMail,
        sender_email_or_email_to_send: str | DraftEmail
    ) -> str:
        """
        Sends a test email to self and returns the UID of the sent email.

        Args:
            openmail (OpenMail): An instance of the OpenMail class.
            sender_email_or_email_to_send (str | DraftEmail): The email address or DraftEmail object to send the test email.

        Returns:
            str: The UID of the sent email.

        Example:
            >>> OpenMailDummyOperator.send_test_email_to_self_and_get_uid(openmail, "someone@domain.com")
            '1'
            >>> OpenMailDummyOperator.send_test_email_to_self_and_get_uid(openmail, DraftEmail(
            ...     sender="someone@domain.com",
            ...     receiver="someone@domain.com",
            ...     subject="test subject",
            ...     body="test body"
            ... ))
            '1'
        """
        print("Sending test email...")

        uid = None
        subject = None
        sender_email = None
        email_to_send = None
        if isinstance(sender_email_or_email_to_send, str):
            subject = NameGenerator.subject()
            sender_email = sender_email_or_email_to_send
            email_to_send = DraftEmail(
                sender_email_or_email_to_send,
                sender_email_or_email_to_send,
                subject,
                NameGenerator.body()
            )
        else:
            subject = sender_email_or_email_to_send.subject
            sender_email = sender_email_or_email_to_send.sender
            email_to_send = sender_email_or_email_to_send

        status, message = openmail.smtp.send_email(email_to_send)

        if not status:
            raise SMTPManagerException(f"Failed to send test email with status: {status} and message: {message}")
        else:
            print("Email sent. Waiting 2 seconds...")
            time.sleep(2)

        status, message = openmail.imap.search_emails(
            folder=Folder.Inbox,
            search=SearchCriteria(
                subject=subject,
                senders=[sender_email],
                receivers=[sender_email]
            )
        )
        if not status:
            raise IMAPManagerException("Failed to search sent email to test email operations with status: ", status, " and message: ", message)
        else:
            print("Test email found...")

        mailbox = openmail.imap.get_emails()
        if len(mailbox.emails) == 0:
            raise IMAPManagerException("Mailbox is empty, failed to test email operations")

        uid = mailbox.emails[0].uid
        if not uid:
            raise IMAPManagerException("Test email not found, failed to test email operations")

        print("Test email sent with uid: ", uid, " subject: ", subject)
        return uid
