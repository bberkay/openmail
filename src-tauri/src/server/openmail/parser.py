"""
Parser Module

This module provides tools for parsing raw email message strings,
typically retrieved from IMAP servers. It includes functionality to
extract message bodies, headers, attachments, and flags, using regular
expressions for precise data extraction. The MessageParser class serves
as the core, offering static methods to handle common email parsing
tasks, while the MessageHeaders type defines the structure of parsed
header fields.
"""
import re
import quopri
from email.header import decode_header
from typing import TypedDict

"""
Types, that are only used in this module
"""
class MessageHeaders(TypedDict):
    """Header fields of a email message."""
    sender: str
    receiver: str
    date: str
    subject: str

"""
Regular expressions, avoid changing
"""
MESSAGE_PATTERN = re.compile(r'\(UID \d+.*?(?=b\'\d+ \(UID|\Z)')
UID_PATTERN = re.compile(r"UID\s+(\d+)")
HEADERS_PATTERN = re.compile(r"BODY\[HEADER\.FIELDS.*?\\r\\n\\r\\n", re.DOTALL)
SENDER_PATTERN = re.compile(r'From:\s+(.+?)(?=\\r\\n\w+:|\\r\\n\\r\\n)', re.DOTALL)
RECEIVER_PATTERN = re.compile(r'To:\s+(.+?)(?=\\r\\n\w+:|\\r\\n\\r\\n)', re.DOTALL)
NAME_EMAIL_PATTERN = re.compile(r"<[^>]+>")
SUBJECT_PATTERN = re.compile(r'Subject:\s+(.*?)(?=\\r\\n\w+:|\\r\\n\\r\\n)', re.DOTALL)
DATE_PATTERN = re.compile(r'Date:\s+(.+?)(?=\\r\\n\w+:|\\r\\n\\r\\n)', re.DOTALL)
BODY_PATTERN = re.compile(r"BODY\[TEXT\].*?b(.*?)(?=\),\s+\(b\'|$)", re.DOTALL)
BODY_TEXT_PATTERN = re.compile(r'Content-Type:\s*text/plain;.*?\\r\\n\\r\\n(.*?)(?=\\r\\n\\r\\n--.*?Content-Type|$)', re.DOTALL | re.IGNORECASE)
ATTACHMENT_PATTERN = re.compile(r'ATTACHMENT.*?\("FILENAME" "([^"]+)"\)', re.DOTALL)
INLINE_ATTACHMENT_CID_PATTERN = re.compile(r'<img src="cid:([^"]+)"', re.DOTALL)
SUPPORTED_EXTENSIONS = r'png|jpg|jpeg|gif|bmp|webp|svg|ico|tiff'
INLINE_ATTACHMENT_DATA_PATTERN = re.compile(r'<img src="data:image/(' + SUPPORTED_EXTENSIONS + r');base64,([^"]+)"', re.DOTALL)
FLAGS_PATTERN = re.compile(r'FLAGS \((.*?)\)', re.DOTALL)
LINE_PATTERN = re.compile(r'(=\\r|\\.*?r\\.*?n)')
SPECIAL_CHAR_PATTERN = re.compile(r'[+\-*/\\|=<>]')
LINK_PATTERN = re.compile(r'https?://[^\s]+|\([^\)]+\)', re.DOTALL)
SPACES_PATTERN = re.compile(r'\s+')

class MessageParser:
    """
    MessageParser class for parsing emails from raw message string.
    It generally used for parsing messages that fetched from IMAP server like this instead of RFC822:
    self.uid('FETCH', "1:4", '(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)] BODY.PEEK[TEXT]<0.500> FLAGS BODYSTRUCTURE)')
    and this fetches returns a list of tuples: [(b'2394 (UID 2651 FLAGS ... ), b'), (b'2395 (UID 2652 FLAGS ... ), b')]
    and before using static methods like `body_from_message()` or `flags_from_message()`, `messages()` should be called
    to get a list of raw messages. It uses regular expressions. So, adding new methods means adding new regular expressions
    nothing else.
    """

    @staticmethod
    def decode_quoted_printable_message(message: str) -> str:
        """
        Decode quoted-printable message. Ignore errors.

        Args:
            message (str): Raw message string.

        Returns:
            str: Decoded message string.

        Example:
            >>> decode_quoted_printable_message("b'(UID ... BODY[TEXT] b'0A=E0=B9=80=E0=B8=A3=E0=B8=B5=E0=B8=A2=
            E0=B8=9' ... b')")
            'สวัสดีชาวโลก' # "Hello World" in Thai
        """
        try:
            decoded_partial_text = quopri.decodestring(message, header=False).decode("utf-8", errors="ignore")
        except Exception as e:
            decoded_partial_text = str(e)

        # If the decoded string ends with "')", remove the last two characters
        # this is occurs when the message is not complete.
        if not "('" in decoded_partial_text:
            decoded_partial_text = decoded_partial_text.endswith("')") and decoded_partial_text[:-2] or decoded_partial_text
        return decoded_partial_text

    @staticmethod
    def decode_utf8_header(message: str) -> str:
        """
        Decode UTF-8 header.

        Args:
            message (str): Raw message string.

        Returns:
            str: Decoded message string.

        Example:
            >>> decode_utf8_header("?UTF-8?B?4LmA4LiC4LmJ4Liy4LiW<noreply@domain.com>4Li24LiH4Lia4LiZ4LiE4Lit4Lih
            4Lie4Li04Lin")
            ชื่อ <noreply@domain.com> # "Name <noreply@domain.com>"
        """
        message = re.split(r'\\r\\n', message)

        decoded_message = ""
        for line in message:
            line = line.strip()
            if line.startswith("=?UTF-8") or line.startswith("=?utf-8"):
                decoded_message += decode_header(line)[0][0].decode('utf-8') + " "
            else:
                decoded_message += line + " "

        return decoded_message.strip()

    @staticmethod
    def messages(message: str) -> list[str]:
        """
        Get messages from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[str]: List of messages.

        Example:
            >>> messages("[(b'2394 (UID 2651 FLAGS ... ), b')', (b'2395 (UID 2652 FLAGS ... ), b')']")
            ['b\'2394 (UID 2651 FLAGS ... ), b\'', 'b\'2395 (UID 2652 FLAGS ... ), b\'']
        """
        return re.findall(MESSAGE_PATTERN, message)

    @staticmethod
    def uid_from_message(message: str) -> str:
        """
        Get UID from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            str: UID string.

        Example:
            >>> uid_from_message("b'2394 (UID 2651 FLAGS ... ), b'")
            '2651'
        """
        uid_match = UID_PATTERN.search(message)
        if uid_match:
            return uid_match.group(1)
        return ""

    @staticmethod
    def body_from_message(message: str) -> str:
        """
        Get body from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            str: Body string.

        Example:
            >>> body_from_message("b'(UID ... BODY[TEXT] b'Hello, World!\\r\\nHow are you?' ... b')")
            'Hello, World! How are you?'
        """
        body_match = BODY_PATTERN.search(message)
        body = ""
        if body_match:
            body = body_match.group(1)

        body_match = BODY_TEXT_PATTERN.search(body)
        if not body_match:
            return ""

        body = body_match.group(1)
        body = bytes(body, "utf-8").decode("unicode_escape")
        body = MessageParser.decode_quoted_printable_message(body)
        body = LINK_PATTERN.sub(' ', body)
        body = LINE_PATTERN.sub(' ', body)
        body = SPECIAL_CHAR_PATTERN.sub(' ', body)
        body = SPACES_PATTERN.sub(' ', body)
        return body.strip()

    @staticmethod
    def attachments_from_message(message: str) -> list[str]:
        """
        Get attachments from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[str]: List of attachments.

        Example:
            >>> attachments_from_message("b'(UID ... ATTACHMENT (FILENAME \"file.txt\") ... ATTACHMENT (FILENAME \"banner.jpg\") b'")
            ['file.txt', 'banner.jpg']
        """
        return ATTACHMENT_PATTERN.findall(message)

    @staticmethod
    def inline_attachment_cids_from_message(message: str) -> list[str]:
        """
        Get inline attachments' cids from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[str]: List of inline attachments.

        Example:
            >>> message = '''
            ... <html>
            ...     <body>
            ...         <p>Check out this image:</p>
            ...         <img src="cid:image1">
            ...         <img src="cid:image2">
            ...     </body>
            ... </html>
            ... '''
            >>> inline_attachment_cids_from_message(message)
            ['image1', 'image2']

        """
        return [match.group(1) for match in INLINE_ATTACHMENT_CID_PATTERN.finditer(message)]

    @staticmethod
    def inline_attachment_data_and_cid_from_message(message: str) -> list[tuple[str, str, int]]:
        # TODO: Look at this later.
        """
        Get inline attachments' data and cid from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[tuple[str, str, int]]: List of inline attachments as extension, data and cid.

        Example:
            >>> message = '''
            ... <html>
            ...     <body>
            ...         <p>Check out this image:</p>
            ...         <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA">
            ...         <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAA">
            ...     </body>
            ... </html>
            ... '''
            >>> inline_attachment_data_and_cid_from_message(message)
            [('png', 'iVBORw0KGgoAAAANSUhEUgAAAAUA', 58),
            ('jpeg', '/9j/4AAQSkZJRgABAQEAAAAAA', 119)]
        """
        return [(match.group(1), match.group(2), match.start()) for match in INLINE_ATTACHMENT_CID_PATTERN.finditer(message)]

    @staticmethod
    def flags_from_message(message: str) -> list[str]:
        """
        Get flags from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[str]: List of flags.

        Example:
            >>> flags_from_message("b'(UID ... FLAGS (\\Seen) ... b'")
            ['\\Seen']
        """
        flags = FLAGS_PATTERN.findall(message)
        return flags[0].replace("\\\\", "\\").replace(",", "").split(" ") if flags and flags[0] else []

    @staticmethod
    def headers_from_message(message: str) -> MessageHeaders:
        """
        Get headers from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            MessageHeaders: Dictionary of headers.

        Example:
            >>> headers_from_message("b'(UID ... FLAGS (\\Seen) ... To: a@gmail.com\\r\\n Subject: Hello\\r\\n Date: 2023-01-01\\r\\n From: b@gmail.com\\r\\n) ... b'")
            {'sender': 'a@gmail.com', 'date': '2023-01-01', 'receiver': 'b@gmail.com', 'subject': 'Hello'}
        """
        header_match = HEADERS_PATTERN.search(message)
        if not header_match:
            return None

        sender = date = subject = receiver = ""
        header_match = header_match.group()

        # Date
        date = DATE_PATTERN.search(header_match)
        date = date.group(1) if date else ""
        date = date.strip()

        # To / Receiver
        receiver = RECEIVER_PATTERN.search(header_match)
        if receiver:
            # If receiver is a name and email like "Alex Wilson <a@gmail.com>"
            # then `email_without_name` will be `a@gmail.com` and `decoded_receiver`
            # will be `Alex Wilson`if receiver is just a email like "a@gmail.com"
            # then `email_without_name` will be None and `decoded_receiver` will
            # be `a@gmail.com`.
            receiver = receiver.group(1)
            receiver = MessageParser.decode_utf8_header(receiver)
            email_without_name = NAME_EMAIL_PATTERN.search(receiver)
            if email_without_name:
                email_without_name = email_without_name.group(0)
                if not email_without_name in receiver:
                    receiver = receiver + " " + email_without_name

        # From / Sender
        sender = SENDER_PATTERN.search(header_match)
        if sender:
            sender = sender.group(1)
            sender = MessageParser.decode_utf8_header(sender)
            email_without_name = NAME_EMAIL_PATTERN.search(sender)
            if email_without_name:
                email_without_name = email_without_name.group(0)
                if not email_without_name in sender:
                    sender = sender + " " + email_without_name

        # Subject
        subject = SUBJECT_PATTERN.search(header_match)
        subject = MessageParser.decode_utf8_header(subject.group(1)) if subject else ""
        subject = SPACES_PATTERN.sub(" ", subject)
        subject = subject.strip()

        return {
            "sender": sender or "",
            "date": date or "",
            "receiver": receiver or "",
            "subject": subject or "",
        }

__all__ = ["MessageParser", "MessageHeaders"]
