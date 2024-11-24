"""
OpenMail Email Client Module

This module provides the OpenMail class, which offers a simplified interface 
for managing email operations via IMAP and SMTP protocols. 
The class supports actions such as connecting to mail servers, sending and 
replying to emails, managing folders, and retrieving email content.

Dependencies:
- Requires `IMAPManager` and `SMTPManager` classes from the `imap` and 
`smtp` modules.

Author: <berkaykayaforbusiness@outlook.com>
License: MIT
"""
import copy
from .types import EmailToSend
from .imap import IMAPManager
from .smtp import SMTPManager, SMTPCommandResult, SMTPManagerException

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
        self.imap = IMAPManager(
            email_address,
            password,
            imap_host,
            imap_port,
            imap_ssl_context,
            timeout
        )
        self.smtp = SMTPManager(
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
        self.smtp.logout()

    def reply_email(self, email: EmailToSend) -> SMTPCommandResult:
        """
        Reply to an existing email. Uses the `send_email` method internally.

        Args:
            email (EmailToSend): The email to be replied to.

        Returns:
            SMTPCommandResult: A tuple containing:
                - A bool indicating whether the email was replied successfully.
                - A string containing a success message or an error message.
        """
        if not email.uid:
            raise SMTPManagerException("Cannot reply to an email without a unique identifier(uid).")
        
        result = self.smtp.reply_email(email)
        if result[0]:
            self.imap.mark_email(email.uid, "answered")

        return result

    def forward_email(self, email: EmailToSend) -> SMTPCommandResult:
        """
        Forward an existing email to new recipients. Uses the `send_email` 
        method internally.

        Args:
            email (EmailToSend): The email to be forwarded.

        Returns:
            SMTPCommandResult: A tuple containing:
                - A bool indicating whether the email was forwarded successfully.
                - A string containing a success message or an error message.
        """
        if not email.uid:
            raise SMTPManagerException("Cannot forward an email without a unique identifier(uid).")
        
        email_fwd_copy = copy.copy(email)
        email_fwd_copy.subject = self.imap.get_email_content(email_fwd_copy.uid).subject
        return self.smtp.forward_email(email_fwd_copy)
    
__all__ = ["OpenMail"]