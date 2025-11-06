import time
from typing import cast

from src.modules.openmail import Openmail
from src.modules.openmail.smtp import SMTPManagerException
from src.modules.openmail.imap import IMAPManagerException
from src.modules.openmail.types import Draft, SearchCriteria, Folder
from tests.modules.openmail.utils.name_generator import NameGenerator

class DummyOperator:
    """Dummy operator for testing purposes."""

    @staticmethod
    def create_test_folder_and_get_name(
        openmail: Openmail,
        folder_name_suffix: str | None = None,
        create_parent: bool = False,
        parent_folder_name_suffix: str | None = None,
    ) -> tuple[str, str]:
        """
        Creates a test folder and returns its name.

        Args:
            openmail (Openmail): An instance of the Openmail class.
            folder_name_suffix (str, optional): The beginning of name of the folder to create.
            If not provided, a random name will be generated.
            create_parent (bool, optional): Whether to create a parent folder. Default is False.
            parent_folder_name_suffix (str, optional): The beginning of name of the parent folder
            to create. If not provided and create_parent is True, a random name will be generated.

        Returns:
            tuple[str, str]: The name of the created folder and it's parent.

        Example:
            >>> OpenmailDummyOperator.create_test_folder_and_get_name(openmail)
            ('openmail-folder-test-uuid', '') # (Child folder, Parent folder)
            >>> OpenmailDummyOperator.create_test_folder_and_get_name(openmail, create_parent=True)
            ('openmail-folder-test-uuid', 'openmail-folder-test-uuid') # (Child folder, Parent folder)
            >>> OpenmailDummyOperator.create_test_folder_and_get_name(
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

        folder_name = folder_name_suffix + NameGenerator.folder_name()[0]

        parent_folder_name = ""
        if create_parent:
            parent_folder_name = parent_folder_name_suffix + NameGenerator.folder_name()[0]

        openmail.imap.create_folder(folder_name, parent_folder_name)
        return (folder_name, parent_folder_name)

    @staticmethod
    def send_test_email_to_self_and_get_uid(
        openmail: Openmail,
        senderOrDraft: str | Draft,
    ) -> str:
        """
        Sends a test email to self and returns the UID of the sent email.

        Args:
            openmail (Openmail): An instance of the Openmail class.
            senderOrDraft (str | Draft): Sender email address like "Name Surname <name@domain.com>" or
            "name@domain.com" or Draft object to send the test email.

        Returns:
            str: The UID of the sent email.

        Example:
            >>> OpenmailDummyOperator.send_test_email_to_self_and_get_uid(openmail, "someone@domain.com")
            '1'
            >>> OpenmailDummyOperator.send_test_email_to_self_and_get_uid(openmail, Draft(
            ...     sender="someone@domain.com",
            ...     receivers="someone@domain.com",
            ...     subject="test subject",
            ...     body="test body"
            ... ))
            '1'
        """
        print("Sending test email...")

        uid = None
        subject = ""
        if isinstance(senderOrDraft, Draft):
            subject = senderOrDraft.subject
        else:
            subject = cast(str, NameGenerator.subject()[0])
            senderOrDraft = Draft(
                sender=senderOrDraft,
                receivers=senderOrDraft,
                subject=subject,
                body=NameGenerator.body()[0]
            )

        status, message = openmail.smtp.send_email(senderOrDraft)

        if not status:
            raise SMTPManagerException(f"Failed to send test email with status: {status} and message: {message}")
        else:
            print("Email sent. Waiting 2 seconds...")
            time.sleep(2)

        openmail.imap.search_emails(
            folder=Folder.Inbox,
            search=SearchCriteria(
                subject=subject,
                senders=[senderOrDraft.sender],
                receivers=[senderOrDraft.receivers] if isinstance(senderOrDraft.receivers, str) else senderOrDraft.receivers
            )
        )

        mailbox = openmail.imap.get_emails()
        if len(mailbox.emails) == 0:
            raise IMAPManagerException("Mailbox is empty, failed to test email operations")

        uid = mailbox.emails[0].uid
        if not uid:
            raise IMAPManagerException("Test email not found, failed to test email operations")

        print("Test email sent with uid: ", uid, " subject: ", subject)
        return uid
