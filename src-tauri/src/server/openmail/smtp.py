import smtplib, re, base64
from typing import List, Tuple, Sequence, MappingProxyType

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from .utils import extract_domain, choose_positive, make_size_human_readable

# General consts
SMTP_SERVERS = MappingProxyType({
    "gmail": "smtp.gmail.com",
    "yahoo": "smtp.mail.yahoo.com",
    "outlook": "smtp-mail.outlook.com",
    "hotmail": "smtp-mail.outlook.com",
    'yandex': 'smtp.yandex.com',
})
SMTP_PORT = 587

# Custom consts
LOGIN_TRY_LIMIT = 3
MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024 # 25MB

# Regular expressions
SUPPORTED_EXTENSIONS = r'png|jpg|jpeg|gif|bmp|webp|svg|ico|tiff'

# Timeouts (in seconds)
CONN_TIMEOUT = 30 

class SmtpManager(smtplib.SMTP):
    """
    SmtpManager extends the `smtplib.SMTP` class to handle email-sending operations
    with added features such as automatic SMTP server detection, retry logic, and
    email composition with attachments.

    Features:
    - Automatic SMTP server detection based on email domain (`__find_smtp_server`).
    - Retry mechanism for login attempts (`login` method).
    - Email sending, replying, and forwarding with metadata support.
    - Attachment validation and inline image support.
    """
    def __init__(
        self, 
        email_address: str, 
        password: str, 
        host: str = "", 
        port: int = SMTP_PORT,
        local_hostname=None,
        timeout: int = CONN_TIMEOUT,
        source_address=None
    ):
        """
        Initialize the SmtpManager class.

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
            timeout=choose_positive(timeout, CONN_TIMEOUT),
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
            raise Exception("Unsupported email domain")

    def login(self, email_address: str, password: str) -> None:
        """
        Perform login to the SMTP server, retrying if necessary.

        Args:
            email_address (str): Email address of the sender.
            password (str): Password for the email account.

        Raises:
            Exception: If login attempts fail.
        """
        try_limit = LOGIN_TRY_LIMIT
        for _ in range(try_limit):
            try:
                self.ehlo()
                self.starttls()
                self.ehlo()
                super().login(email_address, password)
                break
            except Exception as e:
                try_limit -= 1
                if try_limit == 0:
                    raise Exception("Could not connect to the target smtp server: {}".format(str(e)))

    def logout(self) -> None:
        """
        Safely terminate the SMTP session.

        Raises:
            Exception: If the session cannot be terminated.
        """
        try:
            super().quit()
        except Exception as e:
            raise Exception("Could not disconnect from the target smtp server: {}".format(str(e)))

    def __handle_conn(func):
        def wrapper(self, *args, **kwargs):
            try:
                response = func(self, *args, **kwargs)
                return response
            except Exception as e:
                #self.__smtp.quit()
                return False, str(e)
        return wrapper

    #@__handle_conn TODO: Check this
    def sendmail(
        self,
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
        if isinstance(receiver_emails, list):
            receiver_emails = ", ".join(receiver_emails)
        if cc and isinstance(cc, list):
            cc = ", ".join(cc)
        if bcc and isinstance(bcc, list):
            bcc = ", ".join(bcc)

        # sender can be a string(just email) or a tuple (name, email)
        msg = MIMEMultipart()
        msg['From'] = sender if isinstance(sender, str) else f"{sender[0]} <{sender[1]}>"
        msg['To'] = receiver_emails
        msg['Subject'] = subject
        if cc:
            msg['Cc'] = cc
        if msg_metadata:
            for key, value in msg_metadata.items():
                msg[key] = value

        # Attach inline images
        if re.search(r'<img src="data:image/(' + SUPPORTED_EXTENSIONS + r');base64,([^"]+)"', body):
            for match in re.finditer(r'<img src="data:image/(' + SUPPORTED_EXTENSIONS + r');base64,([^"]+)"', body):
                img_ext, img_data = match.group(1), match.group(2)
                cid = f'image{match.start()}'
                body = body.replace(f'data:image/{img_ext};base64,{img_data}', f'cid:{cid}')
                image = base64.b64decode(img_data)
                image = MIMEImage(image, name=f"{cid}.{img_ext}")
                image.add_header('Content-ID', f'<{cid}>')
                msg.attach(image)

        # Create message
        msg.attach(MIMEText(body, 'html'))
        if attachments:
            for attachment in attachments:
                print("Attachment:", attachment.filename)
                if attachment.size > MAX_ATTACHMENT_SIZE:
                    raise Exception("Attachment size is too large. Max size is {}".format(make_size_human_readable(MAX_ATTACHMENT_SIZE)))

                part = MIMEApplication(attachment.file.read())
                part.add_header('content-disposition', 'attachment', filename=attachment.filename)
                msg.attach(part)

        # Handle receipients
        receiver_emails = [email.strip() for email in receiver_emails.split(",")]
        if cc:
            cc = [email.strip() for email in cc.split(",")]
            receiver_emails.extend(cc)
        if bcc:
            bcc = [email.strip() for email in bcc.split(",")]
            receiver_emails.extend(bcc)

        super().sendmail(
            sender if isinstance(sender, str) else sender[1],
            receiver_emails,
            msg.as_string(),
            mail_options,
            rcpt_options
        )

        return True

    def reply_email(self,
        sender: str | Tuple[str, str],
        receiver_emails: str | List[str],
        uid: str,
        subject: str,
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
        return self.sendmail(
            sender,
            receiver_emails,
            "Re: " + subject,
            body,
            attachments,
            None,
            None,
            {
                "In-Reply-To": uid,
                "References": uid
            }
        )

    def forward_email(self,
        sender: str | Tuple[str, str],
        receiver_emails: str | List[str],
        uid: str,
        subject: str,
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
        return self.sendmail(
            sender,
            receiver_emails,
            "Fwd: " + subject,
            body,
            attachments,
            None,
            None,
            {
                "In-Reply-To": uid,
                "References": uid
            }
        )