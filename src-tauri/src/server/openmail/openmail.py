"""
OpenMail
This module provides the OpenMail class, which offers a simplified interface 
for managing email operations via IMAP and SMTP protocols. 

Dependencies:
- Requires `IMAPManager` and `SMTPManager` classes from the `imap` and 
`smtp` modules.

Author: <berkaykayaforbusiness@outlook.com>
License: MIT
"""
import copy
from .types import EmailToSend
from .imap import IMAPManager, Mark
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
        Initialize the OpenMail class.

        Connections will be established when connect() method is called.
        """
        self.__imap = None
        self.__smtp = None

    @property
    def imap(self) -> IMAPManager:
        """Get the IMAPManager instance."""
        return self.__imap

    @property
    def smtp(self) -> SMTPManager:
        """Get the SMTPManager instance."""
        return self.__smtp

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
        self.__imap = IMAPManager(
            email_address,
            password,
            imap_host,
            imap_port,
            imap_ssl_context,
            timeout
        )
        self.__smtp = SMTPManager(
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

__all__ = ["OpenMail"]
