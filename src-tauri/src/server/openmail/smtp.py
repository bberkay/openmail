"""
SMTPManager
This module extends the functionality of the 
`smtplib.SMTP` class to simplify its usage and 
add new features.

Key features include:
- Automated server selection based on email domain.
- Support for attachments, inline images, and metadata in email messages.
- New methods for replying to and forwarding emails.
- Custom error handling, logging.

Primarily designed for use by the `OpenMail` class.

Author: <berkaykayaforbusiness@outlook.com>
License: MIT
"""
import smtplib
import re
import base64
import copy

from typing import override
from types import MappingProxyType

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from .utils import extract_domain, choose_positive, make_size_human_readable
from .types import EmailToSend

# Exceptions
class SMTPManagerException(Exception):
    """Custom exception for SMTPManager class."""
    pass

# Types
type SMTPCommandResult = tuple[bool, str]

# General consts, avoid changing
SMTP_SERVERS = MappingProxyType({
    "gmail": "smtp.gmail.com",
    "yahoo": "smtp.mail.yahoo.com",
    "outlook": "smtp-mail.outlook.com",
    "hotmail": "smtp-mail.outlook.com",
    'yandex': 'smtp.yandex.com',
})
SMTP_PORT = 587

# Custom consts
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024 # 25MB
DEFAULT_CONN_TIMEOUT = 30 # 30 seconds

# Regular expressions, avoid changing
SUPPORTED_EXTENSIONS = r'png|jpg|jpeg|gif|bmp|webp|svg|ico|tiff'
IMG_PATTERN = re.compile(r'<img src="data:image/(' + SUPPORTED_EXTENSIONS + r');base64,([^"]+)"')

class SMTPManager(smtplib.SMTP):
    """
    SMTPManager extends the `smtplib.SMTP` class.
    Does not override any methods except `login`
    and `quit`. Converts `quit` to `logout` for
    consistency with `IMAPManager`. Mainly used
    in `OpenMail` class.
    """
    def __init__(
        self,
        email_address: str,
        password: str,
        host: str = "",
        port: int = SMTP_PORT,
        local_hostname=None,
        timeout: int = DEFAULT_CONN_TIMEOUT,
        source_address=None
    ):
        """
        Initialize the SMTPManager class.

        Args:
            email_address (str): Email address of the sender.
            password (str): Password for the email account.
            host (str, optional): SMTP server address. Defaults to automatic detection.
            port (int, optional): Port for the SMTP server. Defaults to 587.
            local_hostname (str, optional): Local hostname for the connection. Defaults to None.
            timeout (int, optional): Timeout for the connection in seconds. Defaults to 30.
            source_address (tuple, optional): Source address for the connection. Defaults to None.
        """
        super().__init__(
            host or self.__find_smtp_server(email_address),
            port or SMTP_PORT,
            local_hostname=local_hostname,
            timeout=choose_positive(timeout, DEFAULT_CONN_TIMEOUT),
            source_address=source_address
        )

        self.login(email_address, password)

    def __find_smtp_server(self, email_address: str) -> str:
        """
        Find the appropriate SMTP server for a given email address.

        Args:
            email_address (str): Email address of the sender.

        Returns:
            str: SMTP server address.

        Raises:
            Exception: If the email domain is not supported.
        """
        try:
            return SMTP_SERVERS[extract_domain(email_address)]
        except KeyError:
            raise SMTPManagerException("Unsupported email domain") from None

    @override
    def login(self, user: str, password: str, *, initial_response_ok=True) -> SMTPCommandResult:
        """
        Perform login to the SMTP server, retrying if necessary.

        Args:
            email_address (str): Email address of the sender.
            password (str): Password for the email account.

        Raises:
            SMTPManagerException: If the login attempt fails.
        """
        try:
            self.ehlo()
            self.starttls()
            self.ehlo()
            result = super().login(user, password, initial_response_ok=initial_response_ok)
            return (True, str(result))
        except smtplib.SMTPAuthenticationError as e:
            raise SMTPManagerException(f"There was an error while logging in: {str(e)}") from None

    @override
    def quit(self):
        """
        SMTPManager overrides the quit method to perform a safe logout.
        Use `logout` instead.
        """
        pass

    def logout(self) -> SMTPCommandResult:
        """
        Safely terminate the SMTP session.

        Returns:
            SMTPCommandResult: A tuple containing:
                - True
                - A string containing a success message.

        Raises:
            SMTPManagerException: If the logout fails.
        """
        try:
            result = super().quit()
            if str(result[0]) != "221":
                raise SMTPManagerException(f"Could not disconnect from the target smtp server: {str(result)}")
            return (True, "Logout successful")
        except Exception as e:
            raise SMTPManagerException(f"Could not disconnect from the target smtp server: {str(e)}") from None

    def send_email(self, email: EmailToSend) -> SMTPCommandResult:
        """
        Send an email with optional attachments and metadata.

        Args:
            email (EmailToSend): The email to be sent.

        Returns:
            SMTPCommandResult: A tuple containing:
                - A bool indicating whether the email was sent successfully.
                - A string containing a success message or an error message.
        """
        try:
            receiver, cc, bcc = email.receiver, email.cc, email.bcc
            if isinstance(receiver, list):
                receiver = ", ".join(receiver)
            if cc and isinstance(email.cc, list):
                cc = ", ".join(email.cc)
            if bcc and isinstance(email.bcc, list):
                bcc = ", ".join(email.bcc)
        except Exception as e:
            raise SMTPManagerException(f"Error while getting email recipients: {str(e)}") from None

        try:
            # `sender` can be a string(just email) or a tuple (name, email).
            msg = MIMEMultipart()
            msg['From'] = email.sender if isinstance(email.sender, str) else f"{email.sender[0]} <{email.sender[1]}>"
            msg['To'] = receiver
            msg['Subject'] = email.subject
            if cc:
                msg['Cc'] = cc
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email headers: {str(e)}") from None

        try:
            if email.metadata:
                for key, value in email.metadata.items():
                    msg[key] = value
        except Exception as e:
            raise SMTPManagerException(f"Error while adding metadata to headers: {str(e)}") from None

        # Attach inline images.
        try:
            body = email.body
            if IMG_PATTERN.search(body):
                for match in IMG_PATTERN.finditer(body):
                    img_ext, img_data = match.group(1), match.group(2)
                    cid = f'image{match.start()}'
                    body = body.replace(f'data:image/{img_ext};base64,{img_data}', f'cid:{cid}')
                    image = base64.b64decode(img_data)
                    image = MIMEImage(image, name=f"{cid}.{img_ext}")
                    image.add_header('Content-ID', f'<{cid}>')
                    msg.attach(image)
        except Exception as e:
            raise SMTPManagerException(f"Error while handling inline images: {str(e)}") from None

        # Create message and attach attachments.
        try:
            msg.attach(MIMEText(body, 'html'))
            if email.attachments:
                for attachment in email.attachments:
                    if attachment.size > MAX_ATTACHMENT_SIZE:
                        raise SMTPManagerException(f"Attachment size is too large. Max size is {make_size_human_readable(MAX_ATTACHMENT_SIZE)}")

                    part = MIMEApplication(attachment.file.read())
                    part.add_header('content-disposition', 'attachment', filename=attachment.filename)
                    msg.attach(part)
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email message: {str(e)}") from None

        # Handle receipients.
        try:
            receiver = [email.strip() for email in receiver.split(",")]
            if cc:
                cc = [email.strip() for email in cc.split(",")]
                receiver.extend(cc)
            if bcc:
                bcc = [email.strip() for email in bcc.split(",")]
                receiver.extend(bcc)
        except Exception as e:
            raise SMTPManagerException(f"Error while handling email recipients: {str(e)}") from None

        try:
            return super().sendmail(
                email.sender if isinstance(email.sender, str) else email.sender[1],
                receiver,
                msg.as_string(),
                email.mail_options,
                email.rcpt_options
            ) or (True, "Email sent successfully") # `sendmail` func returns empty dict on success.
        except Exception as e:
            raise SMTPManagerException(f"Error, email prepared but could not be sent: {str(e)}") from None

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

        try:
            email_to_reply = copy.copy(email)
            email_to_reply.subject = "Re: " + email.subject
            email_to_reply.metadata = email_to_reply.metadata | {
                "In-Reply-To": email.uid,
                "References": email.uid
            }
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email to reply: {str(e)}") from None

        status, message = self.send_email(email_to_reply)

        # Overriding success message.
        if status:
            return True, "Email replied successfully"

        return status, message

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

        try:
            email_to_forward = copy.copy(email)
            email_to_forward.subject = "Fwd: " + email.subject
            email_to_forward.metadata = email_to_forward.metadata | {
                "In-Reply-To": email.uid,
                "References": email.uid
            }
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email to forward: {str(e)}") from None

        status, message = self.send_email(email_to_forward)

        # Overriding success message.
        if status:
            return True, "Email forwarded successfully"

        return status, message


__all__ = [
    "SMTPManager", 
    "SMTPCommandResult", 
    "SMTPManagerException"
]
