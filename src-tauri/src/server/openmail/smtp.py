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
from typing import Generator, Sequence, cast, override
from types import MappingProxyType
from email.message import EmailMessage, Message
from email.headerregistry import Address
from email.utils import make_msgid
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from .parser import HTMLParser, MessageParser
from .encoder import FileBase64Encoder
from .converter import AttachmentConverter
from .utils import extract_domain, choose_positive, extract_email_address, extract_email_addresses, extract_fullname, extract_username, tuple_to_sender_string
from .types import Draft, Attachment

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

    def send_message(
        self,
        msg: Message,
        from_addr: str | None = None,
        to_addrs: str | Sequence[str] | None = None,
        mail_options: Sequence[str] = (),
        rcpt_options: Sequence[str] = ()
    ) -> SMTPCommandResult:
        try:
            # `send_message` func returns empty dict on success.
            return super().send_message(
                msg,
                from_addr,
                to_addrs,
                mail_options,
                rcpt_options
            ) or (True, "Email sent successfully")
        except Exception as e:
            raise SMTPManagerException(f"Error, email prepared but could not be sent: {str(e)}") from e

    def send_email(self, email: Draft) -> SMTPCommandResult:
        """
        Send an email with optional attachments and metadata.

        Args:
            email (Draft): The email to be sent.

        Returns:
            SMTPCommandResult: A tuple containing:
                - A bool indicating whether the email was sent successfully.
                - A string containing a success message or an error message.
        """
        try:
            all_emails = []
            receivers = set(email.receivers if isinstance(email.receivers, str) else email.receivers)
            receivers = extract_email_addresses(receivers or [])
            all_emails.extend(receivers)
            receivers = ", ".join(receivers)

            cc = None
            if email.cc:
                cc = set(email.cc if isinstance(email.cc, str) else email.cc)
                cc = extract_email_addresses(cc or [])
                cc = [address for address in cc if address not in all_emails]
                all_emails.extend(cc)
                cc = ", ".join(cc)

            bcc = None
            if email.bcc:
                bcc = set(email.bcc if isinstance(email.bcc, str) else email.bcc)
                bcc = extract_email_addresses(bcc or [])
                bcc = [address for address in bcc if address not in all_emails]
                del all_emails
                bcc = ", ".join(bcc)
        except Exception as e:
            raise SMTPManagerException(f"Error while getting email recipients: {str(e)}") from None

        try:
            # `sender` can be a string(just email) or a tuple (name, email).
            msg = EmailMessage()
            msg['From'] = Address(
                display_name=extract_fullname(email.sender),
                username=extract_username(email.sender),
                domain=extract_domain(email.sender, full=True)
            )
            msg['To'] = receivers
            msg['Subject'] = email.subject
            if cc: msg['Cc'] = cc
            if bcc: msg['Bcc'] = bcc
            if email.in_reply_to: msg["In-Reply-To"] = email.in_reply_to
            if email.references: msg["References"] = email.references
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email headers: {str(e)}") from None

        try:
            if email.metadata:
                for key, value in email.metadata.items():
                    msg[key] = value
        except Exception as e:
            print(f"Error while adding metadata to headers: {str(e)} - Skipping metadata.")

        # First payload, text/plain.
        msg.set_content(HTMLParser.parse(email.body))

        # Extract inline attachments, create cid for inline attachments,
        # and change the body with generated cids.
        position_shift = 0
        inline_attachments: list[Attachment] = []
        inline_attachments_cids = set()
        for match in MessageParser.get_inline_attachment_sources(email.body):
            try:
                inline_attachment = None
                src_start, src_value, src_end = match
                src_start, src_end = src_start + position_shift, src_end + position_shift
                inline_attachment = AttachmentConverter.resolve_and_convert(src_value)

                if inline_attachment.size > MAX_INLINE_IMAGE_SIZE:
                    raise SMTPManagerException("Inline image size exceeds the maximum allowed size.")

                src_cid = f"cid:{inline_attachment.cid}"
                email.body = email.body[:src_start] + src_cid + email.body[src_end:]

                position_shift += len(src_cid) - (src_end - src_start)

                if inline_attachment.cid in inline_attachments_cids:
                    print("Duplicate inline images found. Skipping MIME attachment.")
                    continue

                inline_attachments.append(inline_attachment)
                inline_attachments_cids.add(inline_attachment.cid)
            except Exception as e:
                print(f"Error while converting inline attachment to base64 data: `{str(e)}` - Skipping inline image...")

        # Second payload, text/html.
        if HTMLParser.is_html(email.body):
            msg.add_alternative(email.body, subtype="html")

        # Attach inline attachments to `msg` according to their cid number.
        if inline_attachments:
            for inline_attachment in inline_attachments:
                try:
                    related_payload = msg.get_payload()[1]
                    related_payload.add_related(
                        base64.b64decode(
                            inline_attachment.data
                            or
                            FileBase64Encoder.read_file(inline_attachment.path)[3]
                        ),
                        maintype='image',
                        subtype=inline_attachment.type.split('/')[1],
                        cid=f"<{inline_attachment.cid}>",
                        filename=inline_attachment.name,
                        disposition='inline'
                    )
                    related_payload.get_payload(-1).add_header('Content-Length', str(inline_attachment.size))
                except Exception as e:
                    print(f"Error while replacing inline images with cid: `{str(e)}` - Skipping inline image...")

            inline_attachments.clear()

        # Attach attachments to `msg`.
        if email.attachments:
            generated_attachment_cids = set()
            for attachment in email.attachments:
                try:
                    if attachment.cid in generated_attachment_cids:
                        print("Duplicate attachments found. Skipping MIME attachment.")
                        continue

                    if attachment.size > MAX_ATTACHMENT_SIZE:
                        print(f"Attachment size `{attachment.size}` is too large. Max size is {MAX_ATTACHMENT_SIZE} - Skipping MIME attachment.")
                        continue

                    if attachment.data and isinstance(attachment.data, str):
                        attachment.data = base64.b64decode(attachment.data)

                    attachment.data = (
                        attachment.data
                        or
                        base64.b64decode(FileBase64Encoder.read_file(attachment.path)[3])
                    )
                    maintype, subtype = attachment.type.split("/")
                    msg.add_attachment(
                        attachment.data,
                        maintype=maintype,
                        subtype=subtype,
                        cid=attachment.cid,
                        filename=attachment.name,
                    )
                    msg.get_payload(-1).add_header('Content-Length', str(attachment.size))
                    generated_attachment_cids.add(attachment.cid)
                except Exception as e:
                    print(f"Error while creating MIME attachment: `{str(e)}` - Skipping MIME attachment.")

        return self.send_message(msg)

    def reply_email(self,
        original_message_id: str,
        email: Draft,
        original_sender: tuple[str, str] | str = "",
        original_subject: str = "",
        original_body: str = "",
        original_date: str = "",
    ) -> SMTPCommandResult:
        """
        Reply to an existing email. Uses the `send_email` method internally.

        Args:
            email (Draft): The draft email object to send as a reply.
            original_message_id (str): The Message-ID of the email being replied to.
            original_sender (tuple[str, str] | str, optional): The sender of the original email.
            original_subject (str, optional): The subject content of the original email.
            original_body (str, optional): The body content of the original email.
            original_date (str, optional): The date of the original email.

        Returns:
            SMTPCommandResult: A tuple containing:
                - A bool indicating whether the email was replied successfully.
                - A string containing a success message or an error message.
        """
        if not original_message_id:
            raise SMTPManagerException(f"Cannot reply to an email without `original_message_id`.")

        try:
            email_to_reply = copy.copy(email)
            email_to_reply.in_reply_to = original_message_id
            email_to_reply.references = (
                (email_to_reply.references or "") + " " + original_message_id
            ).strip()
            if original_subject: email_to_reply.subject = "Re: " + original_subject
            if original_body:
                email_to_reply.body = f"""
                <div>
                    <div>
                        {email_to_reply.body}
                    </div>
                </div>
                <br/><br/>
                <div>
                    On {original_date}, {tuple_to_sender_string(original_sender)} wrote:<br/>
                    <blockquote style="margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex">
                        {original_body}
                    </blockquote>
                </div>
                """
        except Exception as e:
            raise SMTPManagerException(f"Error while creating email reply: {str(e)}") from None

        status, message = self.send_email(email_to_reply)

        # Overriding success message.
        if status:
            return True, "Email replied successfully"

        return status, message

    def forward_email(self,
        original_message_id: str,
        email: Draft,
        original_sender: tuple[str, str] | str = "",
        original_receivers: str = "", # mail addresses separated by comma
        original_subject: str = "",
        original_body: str = "",
        original_date: str = "",
    ) -> SMTPCommandResult:
        """
        Forward an existing email to new recipients. Uses the `send_email`
        method internally.

        Args:
            email (Draft): The email to be forwarded.
            original_message_id (str): The Message-ID of the email being forwarded.
            original_sender (tuple[str, str] | str, optional): The sender of the original email.
            original_receivers (str, optional): The receivers email addresses of the original
            email (separated by comma).
            original_subject (str, optional): The subject of the original email.
            original_body (str, optional): The body content of the original email.
            original_date (str, optional): The date of the original email.

        Returns:
            SMTPCommandResult: A tuple containing:
                - A bool indicating whether the email was forwarded successfully.
                - A string containing a success message or an error message.
        """
        if not original_message_id:
            raise SMTPManagerException(f"Cannot forward to an email without `original_message_id`.")

        try:
            email_to_forward = copy.copy(email)
            email_to_forward.in_reply_to = original_message_id
            email_to_forward.references = (
                (email_to_forward.references or "") + " " + original_message_id
            ).strip()
            if original_subject: email_to_forward.subject = "Fwd: " + original_subject
            if original_body:
                email_to_forward.body = f"""
                <div>
                    <div>
                        {email_to_forward.body}
                    </div>
                    <br/><br/>
                </div>
                <div>
                    ---------- Forwarded message ----------<br/>
                    {f"From: {tuple_to_sender_string(original_sender)}<br/>" if original_sender else ""}
                    {f"Date: {original_date}<br/>" if original_date else ""}
                    {f"Subject: {original_subject}<br/>" if original_subject else ""}
                    {f"To: {original_receivers}<br/>" if original_receivers else ""}
                    <blockquote style=\"margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex\">
                        {original_body}
                    </blockquote>
                </div>
                """
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
