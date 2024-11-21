import smtplib, re, base64
from typing import List, Tuple, Sequence

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from .utils import extract_domain, choose_positive

SUPPORTED_EXTENSIONS = r'png|jpg|jpeg|gif|bmp|webp|svg|ico|tiff'
SMTP_SERVERS = {
    "gmail": "smtp.gmail.com",
    "yahoo": "smtp.mail.yahoo.com",
    "outlook": "smtp-mail.outlook.com",
    "hotmail": "smtp-mail.outlook.com",
    'yandex': 'smtp.yandex.com',
}

class SMTP(smtplib.SMTP):
    def __init__(self, email_address: str, password: str, host: str = "", port: int = 587, try_limit: int = 3, timeout: int = 30):
        super().__init__(
            host or self.__find_smtp_server(email_address),
            port or 587,
            timeout=choose_positive(timeout, 30)
        )
        self.login(email_address, password, choose_positive(try_limit, 3))

    def __find_smtp_server(self, email_address: str) -> str:
        try:
            return SMTP_SERVERS[extract_domain(email_address)]
        except KeyError:
            raise Exception("Unsupported email domain")

    def login(self, email_address: str, password: str, try_limit: int = 3) -> None:
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

    def quit(self) -> None:
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

    @__handle_conn
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
        Send an email with the given parameters.
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
                if attachment.size > 25 * 1024 * 1024:
                    raise Exception("Attachment size is too large. Max size is 25MB")

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
