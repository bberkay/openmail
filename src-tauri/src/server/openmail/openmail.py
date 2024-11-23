"""
OpenMail Email Client Module

This module provides the OpenMail class, which offers a simplified interface 
for managing email operations via IMAP and SMTP protocols. 
The class supports actions such as connecting to mail servers, sending and 
replying to emails, managing folders, and retrieving email content.

Dependencies:
- Requires `ImapManager` and `SmtpManager` classes from the `imap` and 
`smtp` modules.

Author: <berkaykayaforbusiness@outlook.com>
License: MIT
"""
from typing import List, Tuple, Sequence

from .types import SearchCriteria
from .imap import ImapManager
from .smtp import SmtpManager

class OpenMail:
    """
    A high-level email management class that provides a unified interface 
    for IMAP and SMTP operations.

    This class encapsulates email connection, sending, receiving, 
    and folder management functionality using underlying IMAP and SMTP classes.
    """

    def __init__(self):
        """
        Initialize OpenMail with unestablished IMAP and SMTP connections.
        
        Connections will be established when connect() method is called.
        """
        self.imap = None
        self.smtp = None

    def connect(
        self,
        email_address: str,
        password: str,
        imap_host: str = "",
        imap_port: int = 993,
        imap_ssl_context: any = None,
        smtp_host: str = "",
        smtp_port: int = 587,
        smtp_local_hostname: str = None,
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
        self.imap = ImapManager(
            email_address,
            password,
            imap_host,
            imap_port,
            imap_ssl_context,
            timeout
        )
        self.smtp = SmtpManager(
            email_address,
            password,
            smtp_host,
            smtp_port,
            smtp_local_hostname,
            timeout
        )
        return True, "Connected successfully"

    def disconnect(self) -> None:
        """
        Close both IMAP and SMTP connections.
        """
        self.imap.logout()
        self.__smtp.logout()

    def sendmail(self,
        sender: str | Tuple[str, str],
        receiver_emails: str | List[str],
        subject: str,
        body: str | None = None,
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
        return self.smtp.sendmail(
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
        if self.smtp.reply_email(
            sender,
            receiver_emails,
            uid,
            self.imap.get_email_content(uid)[2]["subject"],
            body,
            attachments
        ):
            self.imap.mark_email(uid, "answered")
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
        return self.smtp.forward_email(
            sender,
            receiver_emails,
            uid,
            self.imap.get_email_content(uid)[2]["subject"],
            body,
            attachments
        )
    