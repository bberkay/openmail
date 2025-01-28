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
import base64
import re
import quopri
from typing import Iterator, Match, TypedDict
from email.header import decode_header
from html.parser import HTMLParser as BuiltInHTMLParser

"""
Regular expressions, avoid changing
"""
MESSAGE_PATTERN = re.compile(r'\(UID \d+.*?(?=b\'\d+ \(UID|\Z)')
SIZE_PATTERN = re.compile(r"RFC822\.SIZE (\d+)")
UID_PATTERN = re.compile(rb"UID\s+(\d+)")
FLEX_LINE_PATTERN = re.compile(rb'(=\r|\.*?r\.*?n)', re.DOTALL)
STRICT_LINE_PATTERN = re.compile(rb'\r\n')
FLAGS_PATTERN = re.compile(rb'FLAGS \((.*?)\)', re.DOTALL | re.IGNORECASE)
TAG_PATTERN = re.compile(r'<[^>]+>')
CID_TAG_PATTERN = re.compile(r'^<|>$')

BODY_PATTERN = re.compile(r"BODY\[TEXT\].*?b(.*?)(?=\),\s+\(b\'|$)", re.DOTALL)
BODY_TEXT_PATTERN = re.compile(r'Content-Type:\s*text/plain;.*?\\r\\n\\r\\n(.*?)(?=\\r\\n\\r\\n--.*?Content-Type|$)', re.DOTALL | re.IGNORECASE)
BODY_TEXT_ENCODING_PATTERN = re.compile(r'Content-Transfer-Encoding:\s*(.+?)\\r\\n', re.DOTALL | re.IGNORECASE)
TEXT_PLAIN_PATTERN = re.compile(rb'Content-Type: text/plain.*?\r\n\r\n(.*?)\r\n\r\n--', re.DOTALL)
TEXT_HTML_PATTERN = re.compile(rb'Content-Type: text/html.*?\r\n\r\n(.*?)\r\n\r\n--', re.DOTALL)
INLINE_ATTACHMENT_DATA_PATTERN = re.compile(rb'Content-ID: <(.*?)>.*?\r\n\r\n(.*?)\r\n\r\n--', re.DOTALL)
ATTACHMENT_PATTERN = re.compile(r'\("([^"]+)"\s+"([^"]+)"\s+NIL\s+"([^"]+)"\s+NIL\s+"[^"]+"\s+(\d+)\s+NIL\s+\("[^"]+"\s+\("FILENAME"\s+"([^"]+)"\)\)\s+NIL\)', re.DOTALL | re.IGNORECASE)
INLINE_ATTACHMENT_CID_PATTERN = re.compile(r'<img src="cid:([^"]+)"', re.DOTALL)
INLINE_ATTACHMENT_FILEPATH_PATTERN = re.compile(r'<img\s+[^>]*src=["\']((?!data:|cid:)[^"\']+)["\']', re.DOTALL | re.IGNORECASE)
INLINE_ATTACHMENT_BASE64_DATA_PATTERN = re.compile(r'data:([a-zA-Z0-9+/.-]+);base64,([a-zA-Z0-9+/=]+)', re.DOTALL | re.IGNORECASE)
INLINE_ATTACHMENT_SRC_PATTERN = re.compile(r'(<img\s+[^>]*src=")(.*?)(")')

SPECIAL_CHAR_PATTERN = re.compile(r'[+\-*/\\|=<>\(]')
LINK_PATTERN = re.compile(r'https?://[^\s]+|\([^\)]+\)', re.DOTALL)
BRACKET_PATTERN = re.compile(r'\[.*?\]')
SPACE_PATTERN = re.compile(r'\s+')

"""
Header Constants
"""
HEADERS_PATTERN = re.compile(rb"BODY\[HEADER\.FIELDS.*?\r\n\r\n", re.DOTALL | re.IGNORECASE)
SUBJECT_PATTERN = re.compile(rb'Subject:\s+(.*?)(?=\r\n\w+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)
SENDER_PATTERN = re.compile(rb'From:\s+(.+?)(?=\r\n\w+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)
RECEIVERS_PATTERN = re.compile(rb'To:\s+(.+?)(?=\r\n\w+:|\r\\n\\r\\n)', re.DOTALL | re.IGNORECASE)
CC_PATTERN = re.compile(rb'Cc:\s+(.*?)(?=\r\n\w+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)
BCC_PATTERN = re.compile(rb'Bcc:\s+(.*?)(?=\r\n\w+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)
REFERENCES_PATTERN = re.compile(rb'References:\s+(.*?)(?=\r\n\w+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)
MESSAGE_ID_PATTERN = re.compile(rb'Message-ID:\s+(.*?)(?=\r\n\w+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)
IN_REPLY_TO_PATTERN = re.compile(rb'In-Reply-To:\s+(.*?)(?=\r\n\w+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)
DATE_PATTERN = re.compile(rb'Date:\s+(.+?)(?=\r\n\w+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)

class MessageHeaders(TypedDict):
    """Header fields of a email message."""
    subject: str
    sender: str
    receivers: str
    date: str
    cc: str
    bcc: str
    in_reply_to: str
    message_id: str
    references: str

MESSAGE_HEADER_PATTERN_MAP = {
    "subject": SUBJECT_PATTERN,
    "sender": SENDER_PATTERN,
    "receivers": RECEIVERS_PATTERN,
    "date": DATE_PATTERN,
    "cc": CC_PATTERN,
    "bcc": BCC_PATTERN,
    "in_reply_to": IN_REPLY_TO_PATTERN,
    "message_id": MESSAGE_ID_PATTERN,
    "references": REFERENCES_PATTERN
}

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
    def decode_base64_message(message: str) -> str:
        """
        Decode base64 message. Ignore errors.

        Args:
            message (str): Raw message string.

        Returns:
            str: Decoded message string.

        Example:
            >>> decode_base64_message("W2ltYWdlOiBHb29nbGVdDQpIZXNhYsSxbsSxemRhIG90dXJ1bSBhw6dtY
            WsgacOnaW4gdXlndWxh")
            'Hello, World'
        """
        return base64.b64decode(message[:-(len(message) % 4)]).decode("utf-8")

    @staticmethod
    def decode_utf8_header(message: bytes) -> str:
        """
        Decode UTF-8 header.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            str: Decoded message string.

        Example:
            >>> decode_utf8_header("?UTF-8?B?4LmA4LiC4LmJ4Liy4LiW<noreply@domain.com>4Li24LiH4Lia4LiZ4LiE4Lit4Lih
            4Lie4Li04Lin")
            ชื่อ <noreply@domain.com>
        """
        decoded_message = ""
        for line in STRICT_LINE_PATTERN.split(message):
            line = str(line).strip()
            if line.startswith("=?UTF-8") or line.startswith("=?utf-8"):
                decoded_lines = decode_header(line)
                for decoded_line in decoded_lines:
                    decoded_message += decoded_line[0].decode("utf-8") + " "
            else:
                decoded_message += line + " "

        return decoded_message.strip()

    @staticmethod
    def decode_filename(message: str) -> str:
        """
        Decode filename.

        Args:
            message (str): Raw message string.

        Returns:
            str: Decoded message string.

        Example:
            >>> decode_filename("['g\\xc3\\xbcnl\\xc3\\xbck rapor.pdf']")
            ['günlük rapor.pdf'] # "Daily Report.pdf" in Turkish
        """
        try:
            decoded = bytes(message, "utf-8").decode("unicode_escape").encode("latin1").decode("utf-8")
            return decoded
        except (UnicodeDecodeError, ValueError):
            return message

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
    def size_from_message(message: str) -> int | None:
        """
        Get size from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            int: Size as bytes.

        Example:
            >>> messages("[b'1430 (UID 1534 RFC822.SIZE 42742)']")
            42742
        """
        match = SIZE_PATTERN.search(message)
        return int(match.group(1)) if match else None

    @staticmethod
    def get_uid(message: bytes) -> str:
        """
        Get UID from raw message bytes.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            str: UID string.

        Example:
            >>> get_uid("b'2394 (UID 2651 FLAGS ... ), b'")
            '2651'
        """
        uid_match = UID_PATTERN.search(message)
        return uid_match.group(1).decode() if uid_match else ""

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

        encoding_match = BODY_TEXT_ENCODING_PATTERN.search(body)

        body = body_match.group(1)
        body = bytes(body, "utf-8").decode("unicode_escape")

        if encoding_match:
            encoding_match = encoding_match.group(1)
            if encoding_match == "quoted-printable":
                body = MessageParser.decode_quoted_printable_message(body)
            elif encoding_match == "base64":
                body = MessageParser.decode_base64_message(body)

        body = LINK_PATTERN.sub(' ', body)
        body = BRACKET_PATTERN.sub(' ', body)
        body = LINE_PATTERN.sub(' ', body)
        body = SPECIAL_CHAR_PATTERN.sub(' ', body)
        body = SPACE_PATTERN.sub(' ', body)

        return body.strip()

    @staticmethod
    def attachments_from_message(message: str) -> list[tuple[str, int, str, str]]:
        """
        Get attachments from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[tuple[str, int, str, str, str]]: List of attachments as (filename, size, cid, mimetype/subtype)

        Example:
            >>> attachments_from_message("b'(BODYSTRUCTURE ... ATTACHMENT (FILENAME \"file.txt\") ... ATTACHMENT (FILENAME \"banner.jpg\") b'")
            [("file.txt", 1029, "bcida...", "APPLICATION/TXT"), ("banner.jpg", 10290, "bcida...", "IMAGE/JPG")]
        """
        return [(match[4], int(match[3]), CID_TAG_PATTERN.sub('', match[2]), f"{match[0]}/{match[1]}".lower(),) for match in ATTACHMENT_PATTERN.findall(message)]

    @staticmethod
    def text_plain_body(message: bytes) -> tuple[int, int, bytes] | None:
        """
        Get plain text from raw message string.

        Args:
            message(bytes): Raw message bytes.

        Returns:
            tuple[int, int, bytes]: Plain text as (start offset, end offset, text itself as bytes)

        Example:
            >>> message = b'''
            ...     ...Content-Type: text/plain; charset="utf-8"
            ...     \r\n...\r\n\r\ntest_send_email_with_attachment
            ...     _and_inline_attachment\r\n\r\nContent-Type...
            ... '''
            >>> text_plain_body(message)
            (42, 74, b"test_send_email_with_attachment_and_inline_attachment")
        """
        text_plain_match = TEXT_PLAIN_PATTERN.search(message)
        if not text_plain_match:
            return None
        start, end = text_plain_match.span()
        return (int(start), int(end), text_plain_match.group(1))

    @staticmethod
    def text_html_body(message: bytes) -> tuple[int, int, bytes] | None:
        """
        Get html text from raw message string.

        Args:
            message(bytes): Raw message bytes.

        Returns:
            tuple[int, int, bytes]: HTML text as (start offset, end offset, text itself as bytes)

        Example:
            >>> message = b'''
            ...     ...Content-Type: text/html; charset="utf-8"...\r\n\r\n
            ...     <html>\r\n<head></head>\r\n<body>\r\n<hr/>\r\n<i>test_s
            ...     end_email_with_attachment_and_inline_attachment<=\r\n/i>\r
            ...     \n<br>\r\n<img src=3D"cid:b89e7b1f7436a0727acf307413310f92"/>
            ...     \r\n<img src=3D"cid:2b07dc3482f143180e8e78d5f9428d67"/>\r\n<hr
            ...     />\r\n</body>\r\n</html>\r\n\r\n\r\b...
            ... '''
            >>> text_html_body(message)
            (
                42,
                74,
                b"<html>
                    <head></head>
                    <body>
                        <hr/>
                        <i>test_send_email_with_attachment_and_inline_attachment</i>
                        <br>
                        <img src=3D"cid:b89e7b1f7436a0727acf307413310f92"/>
                        <img src=3D"cid:2b07dc3482f143180e8e78d5f9428d67"/>
                        <hr/>
                    </body>
                </html>"
            )
        """
        text_html_match = TEXT_HTML_PATTERN.search(message)
        if not text_html_match:
            return None
        start, end = text_html_match.span()
        return (int(start), int(end), text_html_match.group(1))

    @staticmethod
    def inline_attachments_cid_and_data_from_message(message: bytes) -> list[tuple[bytes, bytes]] | None:
        """
        Get inline attachments' data from raw message bytes.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            list[tuple[bytes, bytes]]: List of inline attachment cid and data

        Example:
            >>> message = b'''
            ...    r\n--===============2546737710995511502==\r\nContent-Type: image/png\r\nContent-Transfer-Encoding:
            ...    base64\r\nContent-Disposition: inline; filename="red.png"\r\nContent-ID: <b89e7b1f7436a0727acf307413310f9
            ...    2>\r\nMIME-Version: 1.0\r\nContent-Length: 1243\r\n\r\niVBORw0KGgoAAAANSUhEUgAAAeAAAAEOCAYAAABRmsRnAAAABHNC
            ...    SVQICAgIfAhkiAAAABl0RVh0\r\nU29mdHdhcmUAZ25vbWUtc2NyZWVuc2hvdO8Dvz4AAAAtdEVYdENyZWF0aW9uIFRpbWUAU2F0IDE0...
            ...    Content-Type: image/png\r\nContent-Transfer-Encoding: base64\r\nContent-Disposition: inline; filename="darkblu
            ...    e.png"\r\nContent-ID: <2b07dc3482f143180e8e78d5f9428d67>\r\nMIME-Version: 1.0\r\nContent-Length: 1910\r\n\r\n
            ...    iVBORw0KGgoAAAANSUhEUgAAAnQAAAFxCAYAAAD6TDXhAAAABHNCSVQICAgIfAhkiAAAABl0RVh0\r\nU29mdHdhcmUAZ25vbWUtc2Ny...
            ... '''
            >>> inline_attachments_cid_and_data_from_message(message)
            [
                (b"b89e7b1f7436a0727acf307413310f92", b"iVBORw0KGgoAAAANSUhEUgAAAeAAAAEOCAYAAABRmsRnAAAABHNC..."),
                (b"2b07dc3482f143180e8e78d5f9428d67", b"iVBORw0KGgoAAAANSUhEUgAAAnQAAAFxCAYAAAD6TDXhAAAABHNC..."),
            ]
        """
        return [(cid, data) for cid, data in INLINE_ATTACHMENT_DATA_PATTERN.findall(message)]

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
        matches = INLINE_ATTACHMENT_CID_PATTERN.finditer(message)
        if not matches:
            return []

        return [match.group(1) for match in matches]

    @staticmethod
    def inline_attachment_base64_data_from_message(message: str) -> list[tuple[str, str]]:
        """
        Get inline attachments' base64 data from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[tuple[str, str, int]]: List of inline attachments as extension, data and cid.

        Example:
            >>> message = '''
            ... <html>
            ...     <body>
            ...         <p>Check out this inline files:</p>
            ...         <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA">
            ...         <img src="data:audio/mp3;base64,/9j/4AAQSkZJRgABAQEAAAAAA">
            ...         <img src="data:text/plain;base64,SGVsbG8sIHdvcmxkIQ==">
            ...     </body>
            ... </html>
            ... '''
            >>> inline_attachment_base64_data_from_message(message)
            [('image/png', 'iVBORw0KGgoAAAANSUhEUgAAAAUA'),
             ('audio/mp3', '/9j/4AAQSkZJRgABAQEAAAAAA'),
             ('text/plain', 'SGVsbG8sIHdvcmxkIQ==')]
        """
        matches = INLINE_ATTACHMENT_BASE64_DATA_PATTERN.finditer(message)
        if not matches:
            return []

        return [(match.group(1), match.group(2)) for match in matches]

    @staticmethod
    def inline_attachment_filepath_and_url_from_message(message: str) -> list[str]:
        """
        Get inline attachments' filepath and url from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[str]: List of inline attachments.

        Example:
            >>> message = '''
            ... <html>
            ...     <body>
            ...         <p>Check out this image:</p>
            ...         <img src="mymedia/image1.jpg">
            ...         <img src="https://example.com/mymedia/image2.jpg">
            ...         <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA">
            ...     </body>
            ... </html>
            ... '''
            >>> inline_attachment_filepath_from_message(message)
            ['mymedia/image1.jpg', 'https://example.com/mymedia/image2.jpg']
        """
        matches = INLINE_ATTACHMENT_FILEPATH_PATTERN.finditer(message)
        if not matches:
            return []

        return [match.group(1) for match in matches]

    @staticmethod
    def inline_attachment_src_from_message(message: str) -> list[tuple[int, str, int]]:
        """
        Get inline attachments' src from raw message string.

        Args:
            message (str): Raw message string.

        Returns:
            list[tuple[int, str, int]]: src start position, src value, src end position.

        Example:
            >>> message = '''
            ... <html>
            ...     <body>
            ...         <p>Check out this inline files:</p>
            ...         <img src="image1.png">
            ...         <img src="image2.jpeg">
            ...         <img src="image3.jpg">
            ...     </body>
            ... </html>
            ... '''
            >>> inline_attachment_src_from_message(message)
            [(10, "image1.jpg", 19), (22, "image2.jpg", 29), (32, "image3.jpg", 39)]
        """
        return [(match.start(2), match.group(2), match.end(2)) for match in INLINE_ATTACHMENT_SRC_PATTERN.finditer(message)]

    @staticmethod
    def get_flags(message: bytes) -> list[str]:
        """
        Get flags of `FLAGS` fetch result.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            list[str]: List of flags.

        Example:
            >>> get_flags(b'(UID ... FLAGS (\\Seen \\Flagged) ... b')
            ['\\Seen', '\\Flagged']
        """
        flags = FLAGS_PATTERN.findall(message)
        return flags[0].decode().split(" ") if flags else []

    @staticmethod
    def get_headers(message: bytes) -> MessageHeaders:
        """
        Get headers of `BODY.PEEK[BODY[HEADER.FIELDS (FROM TO SUBJECT DATE CC BCC MESSAGE-ID IN-REPLY-TO REFERENCES)]]`
        fetch result.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            MessageHeaders: Dictionary of headers.

        Example:
            >>> headers_from_message("b'(UID ... FLAGS (\\Seen) ... To: a@gmail.com\\r\\n Subject: Hello\\r\\n Date: 2023-01-01\\r\\n From: b@gmail.com\\r\\n...) ... b'")
            {
                'subject': 'Hello',
                'sender': 'a@gmail.com',
                'receiver': 'b@gmail.com',
                'cc': ''c@gmail.com',
                'bcc': ''d@gmail.com',
                'date': '2023-01-01',
                'in-reply-to': 'e@gmail.com, f@gmail.com',
                'message-id': '<caef..@dom.com>',
                'references': '<5121..@dom.com>'
            }
        """
        message_headers: MessageHeaders = {
            "subject": "",
            "sender": "",
            "receivers": "",
            "cc": "",
            "bcc": "",
            "date": "",
            "in_reply_to": "",
            "message_id": "",
            "references": ""
        }

        header_match = HEADERS_PATTERN.search(message)
        if not header_match:
            return message_headers

        header_match = header_match.group()

        for field_type, field_pattern in MESSAGE_HEADER_PATTERN_MAP.items():
            if field_type == "subject":
                subject = SUBJECT_PATTERN.search(header_match)
                subject = MessageParser.decode_utf8_header(subject.group(1)) if subject else ""
                subject = SPACE_PATTERN.sub(" ", subject)
                subject = subject.strip()
                message_headers["subject"] = subject
            elif field_type in ["references", "in_reply_to", "date", "message_id"]:
                field = field_pattern.search(header_match)
                field = str(field.group(1)) if field else ""
                field = field.strip()
                message_headers[field_type] = field
            elif field_type in ["sender", "receivers", "cc", "bcc"]:
                email_address_match = field_pattern.search(header_match)
                if email_address_match:
                    # If `email_address_match` is a "name <email>" like "Alex Wilson <a@gmail.com>"
                    # then `email_without_name` will be `a@gmail.com` and `decoded_email_address`
                    # will be `Alex Wilson`if receiver is just a email like "a@gmail.com"
                    # then `email_without_name` will be None and `email_address_match` will
                    # be `a@gmail.com`.
                    email_address_match = email_address_match.group(1)
                    email_address_match = MessageParser.decode_utf8_header(email_address_match)
                    email_without_name = TAG_PATTERN.search(email_address_match)
                    if email_without_name:
                        email_without_name = email_without_name.group(0)
                        if not email_without_name in email_address_match:
                            message_headers[field_type] = email_address_match + " " + email_without_name

        return message_headers

class _HTML2TextParser(BuiltInHTMLParser):
    """
    `_HTML2TextParser` is a subclass of `HTMLParser` of `html.parser`.
    This class should not be used directly, instead use `HTMLParser`.
    """
    def __init__(self):
        super().__init__()
        self.text = []
        self._ignore = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self._ignore = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self._ignore = False

    def handle_data(self, data):
        if not self._ignore:
            self.text.append(data.strip())

    def get_text(self) -> str:
        return SPACE_PATTERN.sub(' ', ' '.join(self.text)).strip()

    def parse(self, html: str) -> str:
        self.feed(html)
        return self.get_text()

class HTMLParser():
    """
    This class does not directly parse given html strings,
    instead it creates an instance of `_HTML2TextParser` and
    uses it for parsing operations.
    """
    @staticmethod
    def parse(html: str) -> str:
        """
        Get plain text from given html string.

        Example:
            >>> parse('''
            <html>
              <head><title>Test</title></head>
              <body>
                <script>console.log("Hello");</script>
                <h1>Welcome</h1>
                <p>This is a <b>test</b> page.</p>
                <style>body { color: red; }</style>
              </body>
            </html>
            ''')
            "Welcome This is a test page."
        """
        htmlParser = _HTML2TextParser()
        return htmlParser.parse(html)

    @staticmethod
    def is_html(text: str) -> bool:
        """
        Check if the given text is html.
        Notes:
            - Does not check if it is valid or not.
        Example:
            >>> is_html('''
            <html>
              <head><title>Test</title></head>
              <body>
                <script>console.log("Hello");</script>
                <h1>Welcome</h1>
                <p>This is a <b>test</b> page.</p>
                <style>body { color: red; }</style>
              </body>
            </html>
            ''')
            true
            >>> is_html("<sp>This is a test page")
            true
            >>> is_html("This is a test page")
            false
        """
        return bool(HTML_TAG_PATTERN.search(text))

__all__ = ["HTMLParser", "MessageParser", "MessageHeaders"]
