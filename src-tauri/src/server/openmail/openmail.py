"""
OpenMail Email Client Module

This module provides the OpenMail class, which offers a simplified interface 
for managing email operations via IMAP and SMTP protocols. 
The class supports actions such as connecting to mail servers, sending and 
replying to emails, managing folders, and retrieving email content.

Dependencies:
- Requires `IMAP` and `SMTP` classes from the `imap` and `smtp` modules.

Author: <berkaykayaforbusiness@outlook.com>
License: MIT
"""
from typing import List, Tuple, Sequence

from .types import SearchCriteria
from .imap import IMAP
from .smtp import SMTP

class OpenMail:
    """
    A high-level email management class that provides a unified interface 
    for IMAP and SMTP operations.

    This class encapsulates email connection, sending, receiving, 
    and folder management functionality using underlying IMAP and SMTP classes.

    Attributes:
        __imap (IMAP): Private instance of IMAP for email retrieval operations
        __smtp (SMTP): Private instance of SMTP for email sending operations
    """

    def __init__(self):
        """
        Initialize OpenMail with unestablished IMAP and SMTP connections.
        
        Connections will be established when connect() method is called.
        """
        self.__imap = None
        self.__smtp = None

    def connect(
        self,
        email_address: str,
        password: str,
        imap_host: str = "",
        imap_port: int = 993,
        smtp_host: str = "",
        smtp_port: int = 587,
        try_limit: int = 3,
        timeout: int = 30
    ) -> tuple[bool, str]:
        """
        Establish connections to IMAP and SMTP servers.

        Args:
            email_address (str): Email account username/address
            password (str): Email account password
            imap_host (str, optional): IMAP server hostname. Defaults to "".
            imap_port (int, optional): IMAP server port. Defaults to 993.
            smtp_host (str, optional): SMTP server hostname. Defaults to "".
            smtp_port (int, optional): SMTP server port. Defaults to 587.
            try_limit (int, optional): Number of connection retry attempts. Defaults to 3.
            timeout (int, optional): Connection timeout in seconds. Defaults to 30.

        Returns:
            tuple[bool, str]: A tuple containing connection status (True/False) 
                               and a status message
        """
        self.__imap = IMAP(
            email_address,
            password,
            imap_host,
            imap_port,
            try_limit,
            timeout
        )
        self.__smtp = SMTP(
            email_address,
            password,
            smtp_host,
            smtp_port,
            try_limit,
            timeout
        )
        return True, "Connected successfully"

    def disconnect(self) -> None:
        """
        Close both IMAP and SMTP connections.

        Logs out from IMAP server and quits SMTP connection.
        """
        self.__imap.logout()
        self.__smtp.quit()

    def idle(self) -> None:
        """
        Start IMAP idle mode to listen for new emails.

        This method keeps the connection open and waits for server notifications.
        """
        self.__imap.idle()

    def done(self) -> None:
        """
        Exit IMAP idle mode.

        Terminates the idle state started by idle() method.
        """
        self.__imap.done()

    def send_email(self,
        sender: str | Tuple[str, str],
        receiver_emails: str | List[str],
        subject: str,
        body: str,
        attachments: list | None = None,
        cc: str | List[str] | None = None,
        bcc: str | List[str] | None = None,
        msg_metadata: dict | None = None,
        mail_options: Sequence[str] = (),
        rcpt_options: Sequence[str] = ()
    ) -> bool:
        """
        Send an email with optional attachments and metadata.

        Args:
            sender (str | Tuple[str, str]): Sender's email address or (name, email) tuple
            receiver_emails (str | List[str]): Recipient email address(es)
            subject (str): Email subject line
            body (str): Email body content
            attachments (list, optional): List of file paths to attach. Defaults to None.
            cc (str | List[str], optional): Carbon copy recipient(s). Defaults to None.
            bcc (str | List[str], optional): Blind carbon copy recipient(s). Defaults to None.
            msg_metadata (dict, optional): Additional email headers. Defaults to None.
            mail_options (Sequence[str], optional): SMTP mail options. Defaults to ().
            rcpt_options (Sequence[str], optional): SMTP recipient options. Defaults to ().

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        return self.__smtp.sendmail(
            sender,
            receiver_emails,
            subject,
            body,
            attachments,
            cc,
            bcc,
            msg_metadata,
            mail_options,
            rcpt_options
        )

    def reply_email(self,
        sender: str | Tuple[str, str],
        receiver_emails: str | List[str],
        uid: str,
        body: str,
        attachments: list | None = None
    ) -> bool:
        """
        Reply to an existing email.

        Args:
            sender (str | Tuple[str, str]): Sender's email address or (name, email) tuple
            receiver_emails (str | List[str]): Recipient email address(es)
            uid (str): Unique identifier of the original email being replied to
            body (str): Reply email body content
            attachments (list, optional): List of file paths to attach. Defaults to None.

        Returns:
            bool: True if reply sent successfully and original email marked as answered, 
                  False otherwise
        """
        if self.__smtp.sendmail(
            sender,
            receiver_emails,
            "Re: " + self.__imap.get_email_content(uid)[2]["subject"],
            body,
            attachments,
            None,
            None,
            {
                "In-Reply-To": uid,
                "References": uid
            }
        ):
            self.__imap.mark_email(uid, "answered")
            return True

        return False

    def forward_email(self,
        sender: str | Tuple[str, str],
        receiver_emails: str | List[str],
        uid: str,
        body: str,
        attachments: list | None = None
    ) -> bool:
        """
        Forward an existing email to new recipients.

        Args:
            sender (str | Tuple[str, str]): Sender's email address or (name, email) tuple
            receiver_emails (str | List[str]): Email address(es) to forward to
            uid (str): Unique identifier of the original email being forwarded
            body (str): Forwarding email body content
            attachments (list, optional): List of file paths to attach. Defaults to None.

        Returns:
            bool: True if email forwarded successfully, False otherwise
        """
        return self.__smtp.sendmail(
            sender,
            receiver_emails,
            "Fwd: " + self.__imap.get_email_content(uid)[2]["subject"],
            body,
            attachments,
            None,
            None,
            {
                "In-Reply-To": uid,
                "References": uid
            }
        )
    
    def get_capabilities(self) -> list:
        """
        Retrieve a list of all email folders.

        Returns:
            list: List of folder names in the email account
        """
        return self.__imap.get_capabilities()

    def get_folders(self) -> list:
        """
        Retrieve a list of all email folders.

        Returns:
            list: List of folder names in the email account
        """
        return self.__imap.get_folders()

    def get_folder_status(self, folder: str, status: str = "MESSAGES") -> dict:
        """
        Get status information for a specific email folder.

        Args:
            folder (str): Name of the folder to check
            status (str, optional): Status type to retrieve. Defaults to "MESSAGES".

        Returns:
            dict: Folder status information
        """
        return self.__imap.status(folder, status)

    def get_email_flags(self, uid: str) -> list:
        """
        Retrieve flags associated with a specific email.

        Args:
            uid (str): Unique identifier of the email

        Returns:
            list: List of email flags
        """
        return self.__imap.get_email_flags(uid)

    def get_emails(self,
        folder: str = "inbox",
        search: str | SearchCriteria = "ALL",
        offset: int = 0
    ) -> dict:
        """
        Retrieve emails from a specified folder based on search criteria.

        Args:
            folder (str, optional): Folder to search in. Defaults to "inbox".
            search (str | SearchCriteria, optional): Search criteria. Defaults to "ALL".
            offset (int, optional): Starting index for email retrieval. Defaults to 0.

        Returns:
            dict: Dictionary of emails matching the search criteria
        """
        return self.__imap.get_emails(folder, search, offset)

    def get_email_content(self, uid: str, folder: str = "inbox") -> dict:
        """
        Retrieve full content of a specific email.

        Args:
            uid (str): Unique identifier of the email
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            dict: Detailed email content
        """
        return self.__imap.get_email_content(uid, folder)

    def mark_email(self, uid: str, mark: str, folder: str = "inbox") -> bool:
        """
        Mark an email with a specific flag.

        Args:
            uid (str): Unique identifier of the email
            mark (str): Flag to apply to the email
            folder (str, optional): Folder containing the email. Defaults to "inbox".

        Returns:
            bool: True if email marked successfully, False otherwise
        """
        return self.__imap.mark_email(uid, mark, folder)

    def move_email(self, uid: str, source_folder: str, destination_folder: str) -> bool:
        """
        Move an email from one folder to another.

        Args:
            uid (str): Unique identifier of the email
            source_folder (str): Current folder of the email
            destination_folder (str): Target folder to move the email to

        Returns:
            bool: True if email moved successfully, False otherwise
        """
        return self.__imap.move_email(uid, source_folder, destination_folder)

    def copy_email(self, uid: str, source_folder: str, destination_folder: str) -> bool:
        """
        Create a copy of an email in another folder.

        Args:
            uid (str): Unique identifier of the email
            source_folder (str): Current folder of the email
            destination_folder (str): Target folder to copy the email to

        Returns:
            bool: True if email copied successfully, False otherwise
        """
        return self.__imap.copy_email(uid, source_folder, destination_folder)

    def delete_email(self, uid: str, folder: str) -> bool:
        """
        Delete an email from a specific folder.

        Args:
            uid (str): Unique identifier of the email
            folder (str): Folder containing the email

        Returns:
            bool: True if email deleted successfully, False otherwise
        """
        return self.__imap.delete_email(uid, folder)

    def create_folder(self, folder_name: str, parent_folder: str | None = None) -> bool:
        """
        Create a new email folder.

        Args:
            folder_name (str): Name of the new folder
            parent_folder (str, optional): Parent folder for nested folder creation. 
                                           Defaults to None.

        Returns:
            bool: True if folder created successfully, False otherwise
        """
        return self.__imap.create_folder(folder_name, parent_folder)

    def delete_folder(self, folder_name: str) -> bool:
        """
        Delete an existing email folder.

        Args:
            folder_name (str): Name of the folder to delete

        Returns:
            bool: True if folder deleted successfully, False otherwise
        """
        return self.__imap.delete_folder(folder_name)

    def move_folder(self, folder_name: str, destination_folder: str) -> bool:
        """
        Move a folder to a new location.

        Args:
            folder_name (str): Name of the folder to move
            destination_folder (str): Target location for the folder

        Returns:
            bool: True if folder moved successfully, False otherwise
        """
        return self.__imap.move_folder(folder_name, destination_folder)

    def rename_folder(self, folder_name: str, new_folder_name: str) -> bool:
        """
        Rename an existing email folder.

        Args:
            folder_name (str): Current name of the folder
            new_folder_name (str): New name for the folder

        Returns:
            bool: True if folder renamed successfully, False otherwise
        """
        return self.__imap.rename_folder(folder_name, new_folder_name)