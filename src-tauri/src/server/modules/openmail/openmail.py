"""
Openmail
This module provides the Openmail class, which offers a simplified interface
for managing email operations via IMAP and SMTP protocols.

Dependencies:
- Requires `IMAPManager` and `SMTPManager` classes from the `imap` and
`smtp` modules.

Author: <berkaykayaforbusiness@outlook.com>
License: MIT
"""

from .imap import IMAPManager, IMAPManagerException
from .smtp import SMTPManager, SMTPManagerException


class Openmail:
    """
    A high-level email management class that provides a unified interface
    for IMAP and SMTP operations.

    This class encapsulates email connection, sending, receiving,
    and folder management functionality using underlying IMAP and SMTP classes.
    """

    def __init__(self):
        """
        Initialize the Openmail class.

        Connections will be established when connect() method is called.
        """
        self._imap = None
        self._smtp = None

    @property
    def imap(self) -> IMAPManager:
        """Get the IMAPManager instance."""
        if not self._imap:
            raise IMAPManagerException(
                "IMAP connection is not established. Please call the 'connect' method first."
            )
        return self._imap

    @property
    def smtp(self) -> SMTPManager:
        """Get the SMTPManager instance."""
        if not self._smtp:
            raise SMTPManagerException(
                "SMTP connection is not established. Please call the 'connect' method first."
            )
        return self._smtp

    def connect(
        self,
        email_address: str,
        password: str,
        /,
        *,
        imap_host: str = "",
        imap_port: int = 993,
        imap_ssl_context=None,
        imap_enable_idle_optimization=False,
        imap_listen_new_messages=False,
        smtp_host: str = "",
        smtp_port: int = 587,
        smtp_local_hostname: str | None = None,
        timeout: int = 30,
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
        self._imap = IMAPManager(
            email_address,
            password,
            imap_host,
            imap_port,
            ssl_context=imap_ssl_context,
            timeout=timeout,
            enable_idle_optimization=imap_enable_idle_optimization,
            listen_new_messages=imap_listen_new_messages,
        )
        self._smtp = SMTPManager(
            email_address, password, smtp_host, smtp_port, smtp_local_hostname, timeout
        )
        return True, "Connected successfully"

    def disconnect(self) -> tuple[bool, str]:
        """
        Close both IMAP and SMTP connections.
        """
        imap_stat = smtp_stat = True
        try:
            if self.imap:
                imap_stat, _ = self.imap.logout()
            if self.smtp:
                smtp_stat, _ = self.smtp.logout()
        except IMAPManagerException as e:
            imap_stat = "timeout" in str(e).lower()
        except SMTPManagerException as e:
            smtp_stat = "timeout" in str(e).lower()
        except Exception:
            imap_stat = smtp_stat = False

        disconnect_msg = ""
        if not imap_stat:
            disconnect_msg = "IMAP connection could not terminated properly."
        if not smtp_stat:
            disconnect_msg += "SMTP connection could not terminated properly."
        if disconnect_msg:
            return False, disconnect_msg

        return True, "Disconnected successfully."


__all__ = ["Openmail"]
