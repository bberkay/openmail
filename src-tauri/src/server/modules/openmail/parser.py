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
from typing import NotRequired, TypedDict
from email.header import decode_header
from html.parser import HTMLParser as BuiltInHTMLParser
from collections.abc import MutableSequence

"""
General Fetch Constants
"""
GROUP_PATTERN = re.compile(rb'^\d+ \(UID \d+')
UID_PATTERN = re.compile(rb"UID\s+(\d+)")
APPENDUID_PATTERN = re.compile(br'\[APPENDUID \d+ (\d+)\]')
SIZE_PATTERN = re.compile(rb"RFC822\.SIZE (\d+)")
EXISTS_SIZE_PATTERN = re.compile(rb'\* (\d+) EXISTS')
FLAGS_PATTERN = re.compile(rb'FLAGS \((.*?)\)', re.DOTALL | re.IGNORECASE)
BODYSTRUCTURE_PATTERN = re.compile(r"BODYSTRUCTURE\s+(.*)", re.DOTALL | re.IGNORECASE)
HIERARCHY_DELIMITER_PATTERN = re.compile(rb'\(""\s*"(.?)"\)')
ATTACHMENT_LIST_PATTERN = re.compile(
    r'\("([^"]+)"\s+"([^"]+)"\s+(?:[^\s"]+|\([^\)]+\))\s+"([^"]+)"\s+' \
    r'[^\s"]+\s+"[^"]+"\s+(\d+).*?\("ATTACHMENT"\s+\("FILENAME"\s+' \
    r'"([^"]+)"\)\)\s+[^\s"]+\)',
    re.DOTALL | re.IGNORECASE
)
INLINE_ATTACHMENT_LIST_PATTERN = re.compile(
    r'\("([^"]+)"\s+"([^"]+)"\s+(?:[^\s"]+|\([^\)]+\))\s+"([^"]+)"\s+' \
    r'[^\s"]+\s+"[^"]+"\s+(\d+).*?\("INLINE"\s+\("FILENAME"\s+' \
    r'"([^"]+)"\)\)\s+[^\s"]+\)',
    re.DOTALL | re.IGNORECASE
)

"""
Header Constants
"""
HEADERS_PATTERN = re.compile(rb"BODY\[HEADER\.FIELDS.*?{\d+}", re.DOTALL | re.IGNORECASE)

class MessageHeaders(TypedDict):
    """Header fields of a email message."""
    subject: str
    sender: str
    receivers: str
    date: str
    cc: NotRequired[str]
    bcc: NotRequired[str]
    message_id: NotRequired[str]
    in_reply_to: NotRequired[str]
    references: NotRequired[str]
    list_unsubscribe: NotRequired[str]
    list_unsubscribe_post: NotRequired[str]

MESSAGE_HEADER_PATTERN_MAP = {
    "subject": re.compile(rb'Subject:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "sender": re.compile(rb'From:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "receivers": re.compile(rb'To:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "date": re.compile(rb'Date:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "cc": re.compile(rb'Cc:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "bcc": re.compile(rb'Bcc:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "message_id": re.compile(rb'Message-ID:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "in_reply_to": re.compile(rb'In-Reply-To:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "references": re.compile(rb'References:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "list_unsubscribe": re.compile(rb'List-Unsubscribe:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE),
    "list_unsubscribe_post": re.compile(rb'List-Unsubscribe-Post:\s+(.*?)(?:\r\n[A-Za-z\-]+:|\r\n\r\n)', re.DOTALL | re.IGNORECASE)
}

"""
Body Constants
"""
CONTENT_TYPE_PATTERN = re.compile(
    rb'(?:(?:^|\r\n)Content-Type:\s*([\w\/\-]+))', re.DOTALL | re.IGNORECASE
)
CONTENT_TRANSFER_ENCODING_PATTERN = re.compile(
    rb'(?:(?:^|\r\n)Content-Transfer-Encoding:\s*([\w\/\-]+))', re.DOTALL | re.IGNORECASE
)
BODY_TEXT_PLAIN_OFFSET_AND_ENCODING_PATTERN = re.compile(
    rb'(?:(?:^|\r\n)Content-Type:\s*text/plain(?:(?!\r\n\r\n).)*?\r\nContent-Transfer-Encoding:\s*([\w\-]+))|' \
    rb'(?:(?:^|\r\n)Content-Transfer-Encoding:\s*([\w\-]+)(?:(?!\r\n\r\n).)*?\r\nContent-Type:\s*text/plain)|' \
    rb'(?:(?:^|\r\n)Content-Type:\s*text/plain)',
    re.DOTALL | re.IGNORECASE
)
BODY_TEXT_HTML_OFFSET_AND_ENCODING_PATTERN = re.compile(
    rb'(?:(?:^|\r\n)Content-Type:\s*text/html(?:(?!\r\n\r\n).)*?\r\nContent-Transfer-Encoding:\s*([\w\-]+))|' \
    rb'(?:(?:^|\r\n)Content-Transfer-Encoding:\s*([\w\-]+)(?:(?!\r\n\r\n).)*?\r\nContent-Type:\s*text/html)|' \
    rb'(?:(?:^|\r\n)Content-Type:\s*text/html)',
    re.DOTALL | re.IGNORECASE
)
BODY_TEXT_PLAIN_DATA_PATTERN = re.compile(
    rb'(?:^|\r\n)Content-Type:\s*text/plain.*?\r\n\r\n(.*?)(?=\r\n\r\n|$)',
    re.DOTALL | re.IGNORECASE
)
BODY_TEXT_HTML_DATA_PATTERN = re.compile(
    rb'(?:^|\r\n)Content-Type:\s*text/html.*?\r\n\r\n(.*?)(?=\r\n\r\n|$)',
    re.DOTALL | re.IGNORECASE
)
INLINE_ATTACHMENT_CID_AND_DATA_PATTERN = re.compile(
    rb'(?:^|\r\n)Content-ID: <(.*?)>.*?\r\n\r\n(.*?)\r\n\r\n',
    re.DOTALL
)

"""
Util Constants
"""
LINE_PATTERN = re.compile(r'\r\n')
TAG_PATTERN = re.compile(r'<[^>]+>')
TAG_CLEANING_PATTERN = re.compile(r'^<|>$')
SPECIAL_CHAR_PATTERN = re.compile(r'[+\-*/\\|=<>\(]')
LINK_PATTERN = re.compile(r'https?://[^\s]+|\([^\)]+\)', re.DOTALL)
BRACKET_PATTERN = re.compile(r'\[.*?\]')
SPACE_PATTERN = re.compile(r'\s+')
SRC_PATTERN = re.compile(r'(<img\s+[^>]*src=")(.*?)(")')
INVISIBLE_CHARS = [
    '\u034F',
    '\u2007',
    '\u00AD',
    '\u00A0',
    '\u200B',
    '\u200C',
    '\u200D'
]

class GroupedMessage(MutableSequence):
    def __init__(self, data: list[bytes]):
        self.data = list(data)
        self._create_sorted()

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value
        self._create_sorted()

    def __delitem__(self, index):
        del self.data[index]
        self._create_sorted()

    def __len__(self):
        return len(self.data)

    def insert(self, index, value):
        self.data.insert(index, value)
        self._create_sorted()

    # Special methods

    def _create_sorted(self):
        # TODO: Improve this sorting method
        self._sorted_indexes = [i for i, _ in sorted(enumerate(self.data), key=lambda x: len(x[1]))]

    def sorted(self):
        return [self.data[i] for i in self._sorted_indexes]


class MessageParser:
    """
    MessageParser class for parsing emails from raw message string.
    It generally used for parsing messages that fetched from IMAP server like this instead of RFC822:
    self.uid('FETCH', "1:4", '(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)] BODY.PEEK[TEXT]<0.500>
    FLAGS BODYSTRUCTURE)') and this fetches returns something like this: [(b'2394 (UID 2651 FLAGS ... ),
    b'), (b'2395 (UID 2652 FLAGS ... ), b')] or this: b'Content-Type:text/plain\r\nHello...'. Structure
    of MessageParser is simply regular expressions. So, adding new methods means adding new regular
    expressions.
    """

    @staticmethod
    def group_messages(raw_message: list[bytes | tuple[bytes]]) -> list[GroupedMessage]:
        """
        Group messages of fetch queries like this `(BODY.PEEK[HEADER.FIELDS
        (FROM TO SUBJECT DATE)] BODY.PEEK[TEXT]<0.1024> FLAGS BODYSTRUCTURE)`
        into structured sublists.

        This function processes a list of raw message bytes and groups them
        into sublists. Each sublist contains related message components,
        starting with the byte `b' %d (UID %d` and if it is not found [raw_message]
        will be returned.

        Args:
            raw_message (list[bytes | tuple[bytes]]): A list of raw message byte strings
            representing the components of messages.

        Returns:
            list[GroupedMessage]: A list of grouped message components. Each
            inner list represents a single message, containing its relevant
            parts as byte strings.

        Example:
            >>> raw = [
            ...     (b'2394 (UID 2651 FLAGS ... )',
            ...     b'BODY[HEADER.FIELDS]\\r\\nFrom:a@domain.com'),
            ...     (b'2395 (UID 2652 FLAGS ... )',
            ...     b'BODY[HEADER.FIELDS]\\r\\nFrom:b@domain.com'),
            ... ]
            >>> messages(raw)
            [
                [
                    b'2394 (UID 2651 FLAGS ... ),
                    b'BODY[HEADER.FIELDS]\r\nFrom:a@domain.com'
                ],
                [
                    b'2395 (UID 2651 FLAGS ... ),
                    b'BODY[HEADER.FIELDS]\r\nFrom:b@domain.com'
                ]
            ]
        """
        grouped: list[GroupedMessage] = []
        current: GroupedMessage = GroupedMessage([])

        for part in raw_message:
            if isinstance(part, tuple):
                for part_item in part:
                    if GROUP_PATTERN.match(part_item):
                        if current:
                            grouped.append(current)
                        current = GroupedMessage([part_item])
                    else:
                        current.append(part_item)
            else:
                current.append(part)

        if current:
            grouped.append(current)

        return grouped

    @staticmethod
    def get_part(
        grouped_message: GroupedMessage,
        keywords: list[str],
        case_sensitive = False
    ) -> str | None:
        """
        Extracts the part number from the BODYSTRUCTURE of an email message that matches the provided keywords.

        This method parses the BODYSTRUCTURE response from an IMAP server to locate the specific part
        of the message containing the desired content, such as attachments or specific MIME types.

        Args:
            message (bytes): Raw BODYSTRUCTURE message in bytes, typically from an IMAP fetch response.
            keywords (list[str]): List of keywords to match within the BODYSTRUCTURE, e.g., MIME types or filenames.
            case_sensitive (bool): If True, matching will be case sensitive. Defaults to False.

        Returns:
            str | None: The part number of the message matching the keywords, formatted as a string (e.g., "1", "2.1").
                        Returns None if no matching part is found.

        Example:
            >>> get_part(
            ...     b'... BODYSTRUCTURE ((("TEXT" "PLAIN" ("CHARSET"
            ...     "utf-8") NIL NIL "7BIT" 55 2 NIL NIL NIL) (("TEXT" "... ("IMAGE" "PNG"
            ...     NIL "<b89e7b1f...IL "BASE64" 1704 NIL ("INLINE" ("FILENAME" "red.png"))
            ...     NIL) "RELATED" ("B... "ALTERNATIVE" ("BOUNDARY" ("IMAGE" "PNG" NIL "bf
            ...     7f0...1704 NIL ("ATTACHMENT" ("FILENAME" "black.png")) NIL) "MIXED"
            ...     ("BOUNDARY" "===============3928255875616178789==") NIL NIL),
            ...     ["FILENAME", '"black.png"']
            ... )
            "2"
            >>> get_part(
            ...     b'... BODYSTRUCTURE ((("TEXT" "PLAIN" ("CHARSET"
            ...     "utf-8") NIL NIL "7BIT" 55 2 NIL NIL NIL) (("TEXT" "... ("IMAGE" "PNG"
            ...     NIL "<b89e7b1f...IL "BASE64" 1704 NIL ("INLINE" ("FILENAME" "red.png"))
            ...     NIL) "RELATED" ("B... "ALTERNATIVE" ("BOUNDARY" ("IMAGE" "PNG" NIL "bf
            ...     ... NIL NIL),
            ...     ["TEXT", 'HTML']
            ... )
            "1.2.1"
            >>> get_part(
            ...     b'... BODYSTRUCTURE ("TEXT" "HTML" ("CHARSET" "UTF-8") ... NIL))',
            ...     ["TEXT", "HTML"]
            ... )
            "1"
            >>> get_part(
            ...     b'... BODYSTRUCTURE ("TEXT" "PLAIN" ("CHARSET" "UTF-8") ... NIL))',
            ...     ["TEXT", "PLAIN"]
            ... )
            "1"
        """
        message = ""
        for g_message in grouped_message.sorted():
            message = g_message.decode("utf-8")
            match = BODYSTRUCTURE_PATTERN.search(message)
            if match:
                message = match.group(1)
                break

        if not message:
            return None

        if not case_sensitive:
            message = message.lower()
            keywords = [k.lower() for k in keywords]

        if message[1] != "(":
            if  all(True if keyword in message else False for keyword in keywords):
                return "1"
            else:
                return None

        i = 0
        block = b""
        stack = []
        is_found = False
        start = 0
        for char in message:
            if char == '(':
                stack.append(i)
            elif char == ')':
                if not stack:
                    return None
                start = stack.pop()
                block = message[start: i + 1]
                if block:
                    if all(True if keyword in block else False for keyword in keywords):
                        is_found = True
                        break
            i += 1

        if not is_found:
            return None

        part = "-1"
        i = 0
        s = 0
        while i <= start:
            prev = message[i - 1] if i > 0 else None
            char = message[i]
            next = message[i + 1] if i + 1 <= start else None
            if char == "(":
                s += 1
                inc = int(part[part.rfind(".")+1:]) + 1
                if prev == ")":
                    part = part[:-1]
                    part += str(inc)
                elif next == "(":
                    part = str(inc)
                elif prev == "(":
                    part = part + ".1" if part != "0" else "1"
            elif char == ")":
                s -= 1
                if s == 1:
                    part = part[0]
            i += 1

        return part

    @staticmethod
    def get_uid(grouped_message: GroupedMessage) -> str:
        """
        Get UID from FETCH or APPEND command result.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            str: UID string.

        Example:
            >>> get_uid("b'2394 (UID 2651 FLAGS ... )'")
            '2651'
            >>> get_uid("b'[APPENDUID 6 272] (Success)'")
            '272'
        """
        uid_match = ""
        for message in grouped_message.sorted():
            if b"APPENDUID" in message:
                uid_match = APPENDUID_PATTERN.search(message)
            else:
                uid_match = UID_PATTERN.search(message)

            if not uid_match:
                continue

            return uid_match.group(1).decode()

        return ""

    @staticmethod
    def get_size(grouped_message: GroupedMessage) -> int:
        """
        Get size from `RFC822.SIZE` fetch result.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            int: Size as bytes.

        Example:
            >>> get_size(b'1430 (UID 1534 RFC822.SIZE 42742)')
            42742
        """
        for message in grouped_message.sorted():
            match = SIZE_PATTERN.search(message)
            if not match:
                continue

            return int(match.group(1))

        return -1

    @staticmethod
    def get_exists_size(grouped_message: GroupedMessage) -> int:
        """
        Get size from `EXISTS` server response.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            int: Size as bytes.

        Example:
            >>> get_size(b'* 12 EXISTS')
            12
        """
        for message in grouped_message.sorted():
            match = EXISTS_SIZE_PATTERN.search(message)
            if not match:
                continue

            return int(match.group(1))

        return -1

    @staticmethod
    def get_hierarchy_delimiter(grouped_message: GroupedMessage) -> str:
        """
        Get hierarchy delimiter from `NAMESPACE` server response.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            str: Delimiter.

        Example:
            >>> get_hierarchy_delimiter("b'(("" "/")) NIL NIL'")
            '/'
            >>> get_hierarchy_delimiter("b'(("" ".")) NIL NIL'")
            '.'
        """
        for message in grouped_message.sorted():
            delimiter_match = HIERARCHY_DELIMITER_PATTERN.search(message)
            if not delimiter_match:
                continue

            return delimiter_match.group(1).decode()

        return ""

    @staticmethod
    def get_attachment_list(grouped_message: GroupedMessage) -> list[tuple[str, int, str, str]]:
        """
        Get attachments from `BODYSTRUCTURE` fetch result.

        Args:
            message (str): Raw message bytes.

        Returns:
            list[tuple[str, int, str, str]]: List of attachments as (filename, size, cid, mimetype/subtype)

        Example:
            >>> attachments_from_message(b'(BODYSTRUCTURE ... ATTACHMENT (FILENAME \"file.pdf\")
            ... INLINE (FILENAME \"banner.jpg\") b')
            [("file.txt", 1029, "bcida...", "application/pdf")]
        """
        for message in grouped_message.sorted():
            attachment_list = ATTACHMENT_LIST_PATTERN.findall(message.decode())
            if not attachment_list or not attachment_list[0]:
                continue

            return [
                (
                    match[4],
                    int(match[3]),
                    TAG_CLEANING_PATTERN.sub('', match[2]),
                    f"{match[0]}/{match[1]}".lower()
                )
                for match in attachment_list
            ]

        return []

    @staticmethod
    def get_inline_attachment_list(grouped_message: GroupedMessage) -> list[tuple[str, int, str, str]]:
        """
        Get inline attachments from `BODYSTRUCTURE` fetch result.

        Args:
            message (str): Raw message bytes.

        Returns:
            list[tuple[str, int, str, str]]: List of inline attachments as (filename, size, cid, mimetype/subtype)

        Example:
            >>> attachments_from_message(b'(BODYSTRUCTURE ... ATTACHMENT (FILENAME \"file.txt\")
            ... INLINE (FILENAME \"banner.jpg\") b')
            [("banner.jpg", 10290, "bcida...", "IMAGE/JPG")]
        """
        for message in grouped_message.sorted():
            inline_attachment_list = INLINE_ATTACHMENT_LIST_PATTERN.findall(message.decode())
            if not inline_attachment_list or not inline_attachment_list[0]:
                continue

            return [
                (
                    match[4],
                    int(match[3]),
                    TAG_CLEANING_PATTERN.sub('', match[2]),
                    f"{match[0]}/{match[1]}".lower()
                )
                for match in inline_attachment_list
            ]

        return []

    @staticmethod
    def get_content_type_and_encoding(grouped_message: GroupedMessage) -> tuple[str, str]:
        """
        Extracts the Content-Type and Content-Transfer-Encoding headers from an email message.

        Args:
            message (bytes): The raw email message in bytes.

        Returns:
            tuple[str, str]: Content-Type and Content-Transfer-Encoding values
            as (content_type, encoding)

        Example:
            >>> message = b'''
            ...     ...Content-Type: text/plain; charset="utf-8"
            ...     \r\nContent-Transfer-Encoding: quoted-printable
            ...     \r\n...\r\n\r\ntest_send_email_with_attachment
            ...     _and_inline_attachment\r\n\r\nContent-Type...
            ... '''
            >>> get_content_type_encoding(message)
            ('text/plain', 'quoted-printable')
        """
        for message in grouped_message.sorted():
            content_type_match = CONTENT_TYPE_PATTERN.search(message)
            encoding_match = CONTENT_TRANSFER_ENCODING_PATTERN.search(message)
            if not content_type_match and not encoding_match:
                continue

            content_type = content_type_match.group(1) if content_type_match else b""
            encoding = encoding_match.group(1) if encoding_match else b""
            return content_type.decode(), encoding.decode()

        return "", ""

    @staticmethod
    def get_text_plain_body(grouped_message: GroupedMessage) -> tuple[int, int, str] | None:
        """
        Get plain text from `BODY.PEEK[1]`, `RFC822`, `BODY[TEXT]` etc. fetch results.

        Args:
            message(bytes): Raw message bytes.

        Returns:
            tuple[int, int, str]: Plain text as (start offset, end offset, decoded text)

        Example:
            >>> message = b'''
            ...     ...Content-Type: text/plain; charset="utf-8"
            ...     \r\n...\r\n\r\ntest_send_email_with_attachment
            ...     _and_inline_attachment\r\n\r\nContent-Type...
            ... '''
            >>> get_text_plain_body(message)
            (42, 74, b"test_send_email_with_attachment_and_inline_attachment")
        """
        for message in grouped_message.sorted():
            offset_and_encoding_match = BODY_TEXT_PLAIN_OFFSET_AND_ENCODING_PATTERN.search(message)
            if not offset_and_encoding_match:
                continue

            encoding_start = offset_and_encoding_match.start()
            if not encoding_start:
                continue

            data_match = BODY_TEXT_PLAIN_DATA_PATTERN.search(message[encoding_start:])
            if not data_match:
                continue

            encoding = offset_and_encoding_match.group(1) or offset_and_encoding_match.group(2) or b""
            return (
                *data_match.span(),
                MessageDecoder.body(data_match.group(1), encoding=encoding.decode(), sanitize=True)
            )

        return None

    @staticmethod
    def get_text_html_body(grouped_message: GroupedMessage) -> tuple[int, int, str] | None:
        """
        Get html text from `BODY.PEEK[1]`, `RFC822`, `BODY[TEXT]` etc. fetch results.

        Args:
            message(bytes): Raw message bytes.

        Returns:
            tuple[int, int, bytes]: HTML text as (start offset, end offset, decoded text)

        Example:
            >>> message = b'''
            ...     ...Content-Type: text/html; charset="utf-8"...\r\n\r\n
            ...     <html>\r\n<head></head>\r\n<body>\r\n<hr/>\r\n<i>test_s
            ...     end_email_with_attachment_and_inline_attachment<=\r\n/i>\r
            ...     \n<br>\r\n<img src=3D"cid:b89e7b1f7436a0727acf307413310f92"/>
            ...     \r\n<img src=3D"cid:2b07dc3482f143180e8e78d5f9428d67"/>\r\n<hr
            ...     />\r\n</body>\r\n</html>\r\n\r\n\r\b...
            ... '''
            >>> get_text_html_body(message)
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
        for message in grouped_message.sorted():
            offset_and_encoding_match = BODY_TEXT_HTML_OFFSET_AND_ENCODING_PATTERN.search(message)
            if not offset_and_encoding_match:
                continue

            encoding_start = offset_and_encoding_match.start()
            if not encoding_start:
                continue

            data_match = BODY_TEXT_HTML_DATA_PATTERN.search(message[encoding_start:])
            if not data_match:
                continue

            encoding = offset_and_encoding_match.group(1) or offset_and_encoding_match.group(2)
            return (
                *data_match.span(),
                MessageDecoder.body(data_match.group(1), encoding=encoding.decode())
            )

        return None

    @staticmethod
    def get_cid_and_data_of_inline_attachments(grouped_message: GroupedMessage) -> list[tuple[str, str]]:
        """
        Get inline attachments' data from `BODY.PEEK[1]`, `RFC822`, `BODY.PEEK[TEXT]` etc. fetch results.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            list[tuple[str, str]]: List of inline attachment cid and data

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
            >>> get_cid_and_data_from_inline_attachments(message)
            [
                ("b89e7b1f7436a0727acf307413310f92", "iVBORw0KGgoAAAANSUhEUgAAAeAAAAEOCAYAAABRmsRnAAAABHNC..."),
                ("2b07dc3482f143180e8e78d5f9428d67", "iVBORw0KGgoAAAANSUhEUgAAAnQAAAFxCAYAAAD6TDXhAAAABHNC..."),
            ]
        """
        for message in grouped_message.sorted():
            cid_and_data_match = INLINE_ATTACHMENT_CID_AND_DATA_PATTERN.findall(message)
            if not cid_and_data_match:
                continue

            return [(cid.decode(), data.decode()) for cid, data in cid_and_data_match]

        return []

    @staticmethod
    def get_inline_attachment_sources(message: str) -> list[tuple[int, str, int]]:
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
            >>> get_inline_attachment_sources(message)
            [(10, "image1.jpg", 19), (22, "image2.jpg", 29), (32, "image3.jpg", 39)]
        """
        # TODO: This method shouldn't be in MessageParser
        inline_attachment_sources = SRC_PATTERN.finditer(message)
        if not inline_attachment_sources:
            return []

        return [(int(match.start(2)), match.group(2), int(match.end(2))) for match in inline_attachment_sources]

    @staticmethod
    def get_flags(grouped_message: GroupedMessage) -> list[str]:
        """
        Get flags from `FLAGS` fetch result.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            list[str]: List of flags.

        Example:
            >>> get_flags(b'(UID ... FLAGS (\\Seen \\Flagged) ... b')
            ['\\Seen', '\\Flagged']
        """
        for message in grouped_message.sorted():
            flags = FLAGS_PATTERN.findall(message)
            if not flags:
                continue

            flags = flags[0].decode().strip()
            return flags.split(" ") if flags else []

        return []

    @staticmethod
    def get_headers(grouped_message: GroupedMessage) -> MessageHeaders:
        """
        Get headers from `BODY.PEEK[BODY[HEADER.FIELDS (FROM TO SUBJECT DATE CC BCC MESSAGE-ID
        IN-REPLY-TO REFERENCES)]]`
        fetch result.

        Args:
            message (bytes): Raw message bytes.

        Returns:
            MessageHeaders: Dictionary of headers.

        Example:
            >>> headers_from_message(b'(UID ... FLAGS (\\Seen) ... To: a@gmail.com\r\n Subject: Hello
            ... \r\nDate: 2023-01-01\r\n From: b@gmail.com\\r\\n...) ... b')
            {
                "content_type": "text/plain; charset=utf-8",
                'subject': 'Hello',
                'sender': 'a@gmail.com',
                'receivers': 'b@gmail.com',
                ...
                'message_id': '<caef..@dom.com>',
                'references': '<5121..@dom.com>'
            }
        """
        headers: MessageHeaders = {
            "subject": "",
            "sender": "",
            "receivers": "",
            "date": ""
        }

        message_index_contains_headers = 0
        for i, message in enumerate(grouped_message.sorted()):
            if HEADERS_PATTERN.search(message):
                message_index_contains_headers = i + 1

        for field_type, field_pattern in MESSAGE_HEADER_PATTERN_MAP.items():
            field = field_pattern.search(grouped_message[message_index_contains_headers])
            field = field.group(1) if field else ""
            field = field.decode() if field else ""
            field = MessageDecoder.utf8_header(field)
            field = SPACE_PATTERN.sub(" ", field)
            field = field.strip()

            # Special cases
            if field_type in ["sender", "receivers", "cc", "bcc"]:
                field = field.replace('"', '')

            headers[field_type] = field

        return headers


class MessageDecoder:
    """
    `MessageDecoder` class can be used on its own, but its primary purpose is to
    be used within the `MessageParser` class. It has a structure that ignores errors,
    deficiencies, or redundancies.
    """

    @staticmethod
    def quoted_printable_message(message: str | bytes) -> str:
        """
        Decode quoted-printable message. Ignore errors.

        Args:
            message (str | bytes): Raw message string or bytes.

        Returns:
            str: Decoded message string.

        Example:
            >>> decode_quoted_printable_message(b'(UID ... BODY[TEXT] b'0A=E0=B9=80=E0=B8=A3=E0=B8=B5=E0=B8=A2=
            E0=B8=9')
            'สวัสดีชาวโลก' # "Hello World" in Thai
        """
        if isinstance(message, bytes):
            message = message.decode()

        try:
            decoded_partial_text = quopri.decodestring(message, header=False).decode("utf-8", errors="ignore")
        except Exception as e:
            decoded_partial_text = str(e)

        return decoded_partial_text

    @staticmethod
    def base64_message(message: str | bytes) -> str:
        """
        Decode base64 message. Ignores errors.

        Args:
            message (str | bytes): Raw message string or bytes.

        Returns:
            str: Decoded message string.

        Example:
            >>> decode_base64_message("W2ltYWdlOiBHb29nbGVdDQpIZXNhYsSxbsSxemRhIG90dXJ1bSBhw6dtY
            WsgacOnaW4gdXlndWxh")
            'Hello, World'
        """
        if isinstance(message, bytes):
            message = message.decode()

        try:
            padding = len(message) % 4
            if padding:
                message += '=' * (4 - padding)
            decoded_text = base64.b64decode(message).decode("utf-8", errors="ignore")
        except Exception as e:
            decoded_text = str(e)
        return decoded_text

    @staticmethod
    def utf8_header(message: str | bytes) -> str:
        """
        Decode UTF-8 header.

        Args:
            message (str | bytes): Raw message string or bytes.

        Returns:
            str: Decoded message string.

        Example:
            >>> utf8_header("?UTF-8?B?4LmA4LiC4LmJ4Liy4LiW<noreply@domain.com>4Li24LiH4Lia4LiZ4LiE4Lit4Lih
            4Lie4Li04Lin")
            ชื่อ <noreply@domain.com>
        """
        if isinstance(message, bytes):
            message = message.decode()

        decoded_parts = decode_header(message)
        decoded_string = ''.join([
            part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
            for part, encoding in decoded_parts
        ])
        return decoded_string

    @staticmethod
    def filename(message: str | bytes) -> str:
        """
        Decode filename.

        Args:
            message (str | bytes): Raw message string or bytes.

        Returns:
            str: Decoded message string.

        Example:
            >>> decode_filename("['g\\xc3\\xbcnl\\xc3\\xbck rapor.pdf']")
            ['günlük rapor.pdf'] # "Daily Report.pdf" in Turkish
        """
        if isinstance(message, bytes):
            message = message.decode()

        try:
            decoded = bytes(message, "utf-8").decode("unicode_escape").encode("latin1").decode("utf-8")
            return decoded
        except (UnicodeDecodeError, ValueError):
            return message

    @staticmethod
    def body(message: str | bytes, /, *, encoding: str = "", sanitize: bool = False) -> str:
        """
        Decode and optionally sanitize the message body.

        This method decodes the provided message bytes using the specified encoding.
        Supported encodings are `quoted-printable` and `base64`. If no encoding is provided,
        it defaults to UTF-8 decoding. When `sanitize` is set to `True`, it removes links,
        brackets, special characters, and extra spaces to clean the message content.

        Args:
            message (bytes | str): Raw message string or bytes.
            encoding (str, optional): The encoding type of the message. Supported values are
                "quoted-printable", "base64", or an empty string for plain text. Defaults to "".
            sanitize (bool, optional): If `True`, applies sanitization to remove unnecessary
                characters such as links, brackets, and special symbols. Defaults to `False`.

        Returns:
            str: Decoded (and optionally sanitized) message content.

        Example:
            >>> body(b"SGVsbG8gV29ybGQh", encoding="base64", sanitize=False)
            'Hello World!'

            >>> body(b"Visit our site: https://example.com", sanitize=True)
            'Visit our site'
        """
        if isinstance(message, bytes):
            message = message.decode()

        if encoding == "quoted-printable":
            message = MessageDecoder.quoted_printable_message(message)
        elif encoding == "base64":
            message = MessageDecoder.base64_message(message)

        if sanitize:
            message = ''.join(c for c in message if c not in INVISIBLE_CHARS)
            message = LINK_PATTERN.sub(' ', message)
            message = BRACKET_PATTERN.sub(' ', message)
            message = SPECIAL_CHAR_PATTERN.sub(' ', message)
            message = SPACE_PATTERN.sub(' ', message)
            message = message.strip()

        return message


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
        return bool(TAG_PATTERN.search(text))

__all__ = ["HTMLParser", "MessageParser", "MessageHeaders"]
