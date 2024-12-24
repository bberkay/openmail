"""
SMTPManager
This module extends the functionality of the
`smtplib.SMTP` class to simplify its usage and
add new features.

Key features include:
- Automated server selection based on email domain.
- Support for attachments, inline images, and metadata in email messages.
- New methods for replying to and forwarding emails.
- Custom error handling.

Primarily designed for use by the `OpenMail` class.

Author: <berkaykayaforbusiness@outlook.com>
License: MIT
"""
import base64
import smtplib
import copy

from typing import Generator, override
from types import MappingProxyType

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from .parser import MessageParser
from .encoder import FileBase64Encoder
from .converter import AttachmentConverter
from .utils import extract_domain, choose_positive
from .types import EmailToSend, Attachment

"""
Exceptions
"""
class SMTPManagerException(Exception):
    """Custom exception for SMTPManager class."""
    pass

"""
Types, that are only used in this module
"""
type SMTPCommandResult = tuple[bool, str]

"""
General consts, avoid changing
"""
SMTP_SERVERS = MappingProxyType({
    "gmail": "smtp.gmail.com",
    "yahoo": "smtp.mail.yahoo.com",
    "outlook": "smtp-mail.outlook.com",
    "hotmail": "smtp-mail.outlook.com",
    'yandex': 'smtp.yandex.com',
})
SMTP_PORT = 587

"""
Custom consts
"""
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024 # 25MB
MAX_INLINE_IMAGE_SIZE = 25 * 1024 * 1024 # 25MB
DEFAULT_CONN_TIMEOUT = 30 # 30 seconds

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
            host or self._find_smtp_server(email_address),
            port or SMTP_PORT,
            local_hostname=local_hostname,
            timeout=choose_positive(timeout, DEFAULT_CONN_TIMEOUT),
            source_address=source_address
        )

        self.login(email_address, password)

    def _find_smtp_server(self, email_address: str) -> str:
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
            print(f"Error while adding metadata to headers: {str(e)} - Skipping metadata.")

        body = email.body

        # Extract inline attachments.
        inline_attachments: list[Attachment] = []
        inline_attachment_srcs = MessageParser.inline_attachment_src_from_message(body)
        for match in inline_attachment_srcs:
            try:
                inline_attachment = match.group(2)
                if inline_attachment.startswith("data:"):
                    inline_attachments.append(AttachmentConverter.from_base64(inline_attachment))
                else:
                    inline_attachments.append(AttachmentConverter.resolve_and_convert(inline_attachment))
            except Exception as e:
                print(f"Error while converting inline attachment to base64 data: `{str(e)}` - Skipping inline image...")

        # Create MIME attachments from inline attachments
        # and replace inline images with cid.
        if inline_attachments:
            generated_inline_attachment_cids = set()
            for i, match in enumerate(reversed(inline_attachment_srcs)):
                try:
                    if inline_attachments[i].size > MAX_INLINE_IMAGE_SIZE:
                        raise SMTPManagerException("Inline image size exceeds the maximum allowed size.")

                    body = body[:match.start(2)] + f"cid:{inline_attachments[i].cid}" + body[match.end(2):]

                    if inline_attachments[i].cid in generated_inline_attachment_cids:
                        print("Duplicate inline images found. Skipping MIME attachment.")
                        continue

                    image = base64.b64decode(
                        inline_attachments[i].data or FileBase64Encoder.read_file(inline_attachments[i].path)[3]
                    )
                    image = MIMEImage(image, name=f"{inline_attachments[i].cid}.{inline_attachments[i].type.split('/')[1]}")
                    image.add_header('Content-Id', f'<{inline_attachments[i].cid}>')
                    image.add_header('Content-Disposition', 'inline')
                    image.add_header('Content-Type', f'{inline_attachments[i].type}')
                    image.add_header('Content-Transfer-Encoding', 'base64')
                    msg.attach(image)
                    generated_inline_attachment_cids.add(inline_attachments[i].cid)
                except Exception as e:
                    print(f"Error while replacing inline images with cid: `{str(e)}` - Skipping inline image...")

            inline_attachment_srcs.clear()
            inline_attachments.clear()

        try:
            msg.attach(MIMEText(body, 'html'))
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email message body: {str(e)}") from e

        # Attach attachments
        if email.attachments:
            generated_attachment_cids = set()
            for attachment in email.attachments:
                try:
                    attachment = AttachmentConverter.resolve_and_convert(attachment)
                    if attachment.cid in generated_attachment_cids:
                        print("Duplicate attachments found. Skipping MIME attachment.")
                        continue

                    if attachment.size > MAX_ATTACHMENT_SIZE:
                        print(f"Attachment size `{attachment.size}` is too large. Max size is {MAX_ATTACHMENT_SIZE} - Skipping MIME attachment.")
                        continue

                    part = MIMEApplication(base64.b64decode(
                        attachment.data or FileBase64Encoder.read_file(attachment.path)[3]
                    ))
                    part.add_header('Content-Id', attachment.cid)
                    part.add_header('Content-Disposition', 'attachment', filename=attachment.name)
                    part.add_header('Content-Transfer-Encoding', 'base64')
                    part.add_header('Content-Type', attachment.type)
                    part.add_header('Content-Length', str(attachment.size))
                    msg.attach(part)
                    generated_attachment_cids.add(attachment.cid)
                except Exception as e:
                    print(f"Error while creating MIME attachment: `{str(e)}` - Skipping MIME attachment.")

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
            raise SMTPManagerException(f"Error, email prepared but could not be sent: {str(e)}") from e

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
            raise SMTPManagerException(f"Cannot reply to an email without a unique identifier(uid).")

        try:
            email_to_reply = copy.copy(email)
            email_to_reply.subject = "Re: " + email.subject
            email_to_reply.metadata = email_to_reply.metadata | {
                "In-Reply-To": email.uid,
                "References": email.uid
            }
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email reply: {str(e)}") from None

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
            raise SMTPManagerException(f"Cannot forward an email without a unique identifier(uid).")

        try:
            email_to_forward = copy.copy(email)
            email_to_forward.subject = "Fwd: " + email.subject
            email_to_forward.metadata = email_to_forward.metadata | {
                "In-Reply-To": email.uid,
                "References": email.uid
            }
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email to forward: `{str(e)}`") from None

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
