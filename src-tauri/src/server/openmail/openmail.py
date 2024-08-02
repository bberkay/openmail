import re, base64
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, TypedDict, Tuple

import email
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from .utils import convert_to_imap_date, make_size_human_readable
from .imap import IMAP
from .smtp import SMTP
from .types import SearchCriteria

SUPPORTED_EXTENSIONS = r'png|jpg|jpeg|gif|bmp|webp|svg|ico|tiff'
CID_RE_COMPILE = re.compile(r'<img src="cid:([^"]+)"')

class OpenMail:
    def __init__(self, email_address: str, password: str, imap_port: int = 993, smtp_port: int = 587, try_limit: int = 3, timeout: int = 30):
        self.__imap = IMAP(email_address, password, imap_port, try_limit, timeout)
        self.__smtp = SMTP(email_address, password, smtp_port, try_limit, timeout)

    def __handle_smtp_conn(func):
        def wrapper(self, *args, **kwargs):
            try:
                self.__smtp.login()
                response = func(self, *args, **kwargs) # type: ignore
                return response
            except Exception as e:
                return False, str(e)
            finally:
                self.__smtp.quit()
        return wrapper

    def __handle_imap_conn(func):
        def wrapper(self, *args, **kwargs):
            try:
                self.__imap.login()
                response = func(self, *args, **kwargs) # type: ignore
                return response
            except Exception as e:
                return False, str(e)
            finally:
                self.__imap.logout()
        return wrapper

    def __encode_folder(self, folder: str) -> str:
        return ('"' + folder + '"').encode("utf-8")

    def __decode_folder(self, folder: bytes) -> str:
        return folder.decode().split(' "/" ')[1].replace('"', '')

    @__handle_smtp_conn
    def __send_email(self, sender: str | Tuple[str, str], receiver_emails: str | List[str], subject: str, body: str, attachments: list | None = None, msg_meta: dict | None = None) -> tuple[bool, str]:
        if isinstance(receiver_emails, list):
            receiver_emails = ", ".join(receiver_emails)

        # sender can be a string(just email) or a tuple (name, email)
        msg = MIMEMultipart()
        msg['From'] = sender if isinstance(sender, str) else f"{sender[0]} <{sender[1]}>"
        msg['To'] = receiver_emails
        msg['Subject'] = subject
        if msg_meta:
            for key, value in msg_meta.items():
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

        msg.attach(MIMEText(body, 'html'))
        if attachments:
            for attachment in attachments:
                print("Attachment:", attachment.filename)
                if attachment.size > 25 * 1024 * 1024:
                    return False, "Attachment size limit is 25 MB"

                part = MIMEApplication(attachment.file.read())
                part.add_header('content-disposition', 'attachment', filename=attachment.filename)
                msg.attach(part)

        # receiver_emails can be a string or
        self.__smtp.sendmail(
            sender if isinstance(sender, str) else sender[1],
            [email.strip() for email in receiver_emails.split(",")],
            msg.as_string()
        )
        return True, "Email sent successfully"

    def send_email(self, sender: str | Tuple[str, str], receiver_emails: str | List[str], subject: str, body: str, attachments: list | None = None) -> tuple[bool, str]:
        return self.__send_email(
            sender,
            receiver_emails,
            subject,
            body,
            attachments
        )

    def reply_email(self, sender: str | Tuple[str, str], receiver_emails: str | List[str], uid: str, body: str, attachments: list | None = None) -> tuple[bool, str]:
        result = self.__send_email(
            sender,
            receiver_emails,
            "Re: " + self.get_email_content(uid)[2]["subject"],
            body,
            attachments,
            {
                "In-Reply-To": uid,
                "References": uid
            }
        )

        if result[0]:
            self.mark_email(uid, "answered")

        return result

    def forward_email(self, sender: str | Tuple[str, str], receiver_emails: str | List[str], uid: str, body: str, attachments: list | None = None) -> tuple[bool, str]:
        return self.__send_email(
            sender,
            receiver_emails,
            "Fwd: " + self.get_email_content(uid)[2]["subject"],
            body,
            attachments,
            {
                "In-Reply-To": uid,
                "References": uid
            }
        )

    @__handle_imap_conn
    def get_folders(self) -> tuple[bool, str, list] | tuple[bool, str]:
        return True, "Folders fetched successfully", [self.__decode_folder(i) for i in self.__imap.list()[1]]

    def __fetch_flags(self, uid: str) -> list:
        if self.__imap.state != "SELECTED":
            raise Exception("Folder should be selected before fetching flags")

        flags = self.__imap.uid('FETCH', uid, '(FLAGS)')[1][0]
        if flags:
            flags = flags.decode()
            flags = re.findall(r'\\([a-zA-Z]+)', flags)
        return flags or []

    def __build_search_criteria_query(self, search_criteria: SearchCriteria) -> str:
        """
            Preparing to convert search_json to search_criteria string:
            https://datatracker.ietf.org/doc/html/rfc9051#name-search-command
        """

        def recursive_or_query(criteria: str, search_keys: List[str]) -> str:
            """
            Example:
                search_keys = ["johndoe@mail.com", "janedoe@mail.com", "person@mail.com"]
                return: 'OR (FROM "johndoe@mail.com") (OR (FROM "janedoe@mail.com") (FROM "person@mail.com"))'
            """
            query = ''
            len_search_keys = len(search_keys)
            if len_search_keys == 1:
                return f'{criteria} "{search_keys[0]}"'

            mid = len_search_keys // 2
            left_part = recursive_or_query(criteria, search_keys[:mid])
            right_part = recursive_or_query(criteria, search_keys[mid:])

            return query + f'OR ({left_part}) ({right_part})'

        def add_criterion(criteria: str, value: str | list, seperate_with_or: bool = False) -> str:
            if not value:
                return ''

            if isinstance(value, list):
                if criteria == '':
                    # value=["Flagged", "Seen", "Answered"]
                    return ' '.join([i.upper() for i in value])

                if len(value) <= 1:
                    return f' ({criteria} "{value[0]}")'

            if seperate_with_or and len(value) > 1:
                criteria = ''
                value = recursive_or_query(criteria, value)

            return f' ({criteria} "{value}")'

        search_criteria_query = ''
        search_criteria_query += add_criterion('FROM', search_criteria.senders, len(search_criteria.senders) > 1)
        search_criteria_query += add_criterion('TO', search_criteria.receivers, len(search_criteria.receivers) > 1)
        search_criteria_query += add_criterion("SUBJECT", search_criteria.subject)
        search_criteria_query += add_criterion("SINCE", search_criteria.since)
        search_criteria_query += add_criterion("BEFORE", search_criteria.before)
        search_criteria_query += add_criterion("TEXT", search_criteria.include)
        search_criteria_query += add_criterion("NOT TEXT", search_criteria.exclude)
        search_criteria_query += add_criterion('', search_criteria.flags)
        return search_criteria_query.strip()

    def __search_with_criteria(self, criteria: str) -> list:
        if self.__imap.state != "SELECTED":
            raise Exception("Folder should be selected before searching")

        _, uids = self.__imap.uid('search', None, criteria.encode("utf-8"))
        return uids[0].split()[::-1] if uids else []

    @__handle_imap_conn
    def get_emails(self, folder: str = "inbox", search: str | SearchCriteria = "ALL", offset: int = 0) -> tuple[bool, str, dict] | tuple[bool, str]:
        self.__imap.select(self.__encode_folder(folder), readonly=True)

        search_criteria_query = ''
        must_have_attachment = False
        if isinstance(search, SearchCriteria):
            must_have_attachment = search.has_attachments
            search_criteria_query = self.__build_search_criteria_query(search) or 'ALL'
        else:
            search_criteria_query = search

        uids = self.__search_with_criteria(search_criteria_query)

        if len(uids) == 0:
            return True, "No emails found", {"folder": folder, "emails": [], "total": 0}

        emails = []
        for uid in uids[offset: offset + 10]:
            """
            _, data = M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (CONTENT-TYPE)])')
            if b"multipart/mixed" in data[0][1]:
                print("Found multipart/mixed: ", num
            """
            _, message = self.__imap.uid('fetch', uid, '(RFC822)')
            message = email.message_from_bytes(message[0][1], policy=email.policy.default)

            payload = [message]
            if message.is_multipart():
                if must_have_attachment and message.get_content_type() != "multipart/mixed":
                    continue
                payload = message.walk()

            body = ""
            is_body_html = False
            for part in payload:
                content_type = part.get_content_type()
                file_name = part.get_filename()

                is_body_html = content_type == "text/html"
                if (file_name is None and content_type == "text/plain") or (is_body_html and not body):
                    body = part.get_payload(decode=True)
                    body = body.decode(part.get_content_charset() or "utf-8") if body else ""

            body = BeautifulSoup(body, "html.parser").get_text() if is_body_html else body
            body = re.sub(r'<br\s*/?>', '', body).strip() if body != b'' else ""
            body = re.sub(r'[\n\r\t]+| +', ' ', body).strip()

            emails.append({
                "uid": uid.decode(),
                "from": message["From"],
                "to": message["To"] if "To" in message else "",
                "subject": message["Subject"],
                "body_short": (body if body != "" else "No Content") if len(body) < 50 else body[:50] + "...",
                "date": datetime.strptime(message["Date"], "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S"),
                "flags": self.__fetch_flags(uid) or []
            })

        return True, "Emails fetched successfully", {"folder": folder, "emails": emails, "total": len(uids)}

    @__handle_imap_conn
    def get_email_content(self, uid: str, folder: str = "inbox") -> tuple[bool, str, dict] | tuple[bool, str]:
        self.__imap.select(self.__encode_folder(folder), readonly=True)

        _, message = self.__imap.uid('fetch', uid, '(RFC822)')
        message = email.message_from_bytes(message[0][1], policy=email.policy.default)

        body, attachments = "", []
        for part in (message.walk() if message.is_multipart() else [message]):
            content_type = part.get_content_type()
            file_name = part.get_filename()
            if file_name:
                attachments.append({
                    "cid": part.get("X-Attachment-Id"),
                    "name": file_name,
                    "data": base64.b64encode(part.get_payload(decode=True)).decode("utf-8", errors="ignore"),
                    "size": make_size_human_readable(len(part.get_payload(decode=True))),
                    "type": content_type
                })
            elif content_type == "text/html" or (content_type == "text/plain" and not body):
                body = part.get_payload(decode=True)
                if body:
                    body = body.decode(part.get_content_charset())

        if attachments:
            for match in CID_RE_COMPILE.finditer(body):
                cid = match.group(1)
                for attachment in attachments:
                    if cid in attachment["name"] or cid in attachment["cid"]:
                        body = body.replace(f'cid:{cid}', f'data:{attachment["type"]};base64,{attachment["data"]}')

        if "Seen" not in self.__fetch_flags(uid):
            self.mark_email(uid, "seen", folder)

        return True, "Email fetched successfully", {
            "uid": uid,
            "from": message["From"],
            "to": message["To"] if "To" in message else "",
            "subject": message["Subject"],
            "body": body,
            "date": datetime.strptime(message["Date"], "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S"),
            "flags": self.__fetch_flags(uid) or [],
            "attachments": attachments
        }

    @__handle_imap_conn
    def mark_email(self, uid: str, mark: str, folder: str = "inbox") -> tuple[bool, str]:
        self.__imap.select(self.__encode_folder(folder))

        mark = mark.lower()
        mark_type = "-" if mark[0] + mark[1] == "un" else "+"
        mark = mark[2:] if mark_type == "-" else mark
        command = mark_type + "FLAGS"

        # https://datatracker.ietf.org/doc/html/rfc9051#name-flags-message-attribute
        mark_map = {
            "flagged": "\\Flagged",
            "seen": "\\Seen",
            "answered": "\\Answered",
            #"deleted": "\\Deleted",
            #"draft": "\\Draft",
            #"spam": "\\Spam"
        }

        if mark not in mark_map:
            return False, "Invalid mark"

        self.__imap.uid('STORE', uid, command, mark_map[mark])
        self.__imap.expunge()
        return True, "Email marked successfully"

    @__handle_imap_conn
    def move_email(self, uid: str, source_folder: str, destination_folder: str) -> tuple[bool, str]:
        self.__imap.select(self.__encode_folder(source_folder))
        self.__imap.uid('COPY', uid, self.__encode_folder(destination_folder))
        self.__imap.uid('STORE', uid , '+FLAGS', '(\Deleted)')
        self.__imap.expunge()
        return True, "Email moved successfully"

    @__handle_imap_conn
    def delete_email(self, uid: str, folder: str) -> tuple[bool, str]:
        # If current folder isn't the trash bin, move it to the trash bin.
        self.__imap.select(self.__encode_folder(folder))
        self.__imap.uid('STORE', uid , '+FLAGS', '(\Deleted)')
        self.__imap.expunge()
        # TODO: Select the trash bin and delete it from there.
        return True, "Email deleted successfully"

    @__handle_imap_conn
    def create_folder(self, folder_name: str, parent_folder: str | None = None) -> tuple[bool, str]:
        if parent_folder:
            folder_name = f"{parent_folder}/{folder_name}"
        self.__imap.create(self.__encode_folder(folder_name))
        return True, "Folder created successfully"

    @__handle_imap_conn
    def delete_folder(self, folder_name: str) -> tuple[bool, str]:
        self.__imap.delete(self.__encode_folder(folder_name))
        return True, "Folder deleted successfully"

    @__handle_imap_conn
    def move_folder(self, folder_name: str, destination_folder: str) -> tuple[bool, str]:
        if "/" in folder_name:
            destination_folder = f"{destination_folder}/{folder_name.split("/")[-1]}"
        self.__imap.rename(self.__encode_folder(folder_name), self.__encode_folder(destination_folder))
        return True, "Folder moved successfully"

    @__handle_imap_conn
    def rename_folder(self, folder_name: str, new_folder_name: str) -> tuple[bool, str]:
        if "/" in folder_name:
            new_folder_name = folder_name.replace(folder_name.split("/")[-1], new_folder_name)
        self.__imap.rename(self.__encode_folder(folder_name), self.__encode_folder(new_folder_name))
        return True, "Folder renamed successfully"
