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
import email
from typing import TypedDict

# Custom types
class MessageHeaders(TypedDict):
    """Header fields of a email message."""
    sender: str
    receiver: str
    date: str
    subject: str

# Regular expressions, avoid changing
MESSAGE_PATTERN = re.compile(r"(b'\d+ \(UID \d+ .+?b'\))")
HEADERS_PATTERN = re.compile(r"\(b' BODY\[HEADER\.FIELDS.*?\), b'\)")
SENDER_PATTERN = re.compile(r'From:\s+(.+?)\\r\\n')
RECEIVER_PATTERN = re.compile(r'To:\s+(.+?)\\r\\n')
SUBJECT_PATTERN = re.compile(r'Subject:\s*(.*?)\\r\\n')
DATE_PATTERN = re.compile(r'Date:\s+(.+?)\\r\\n')
BODY_PATTERN = re.compile(r"BODY\[TEXT\].*?b'(.*?)\), \(b' BODY\[HEADER")
BODY_TEXT_PATTERN = re.compile(r'(?i)Content-Type: text/plain; charset="utf-8".*?\\r\\n\\r\\n(.*?)(?=\\r\\n\\r\\n--[^-]|$)')
ATTACHMENT_PATTERN = re.compile(r'ATTACHMENT.*?\("FILENAME" "([^"]+)"\)') 
INLINE_ATTACHMENT_PATTERN = re.compile(r'<img src="cid:([^"]+)"')
FLAGS_PATTERN = re.compile(r'FLAGS \((.*?)\)')
LINE_PATTERN = re.compile(r'\\.*?r\\.*?n')
PLAIN_TEXT_PATTERN = re.compile(r'=[A-Za-z0-9]+|\(.*?\)|\*+|-+|\s+')
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

        body_match = BODY_TEXT_PATTERN.search(body, re.DOTALL)
        if not body_match:
            return ""
        
        body = body_match.group(1)    
        body = LINE_PATTERN.sub(' ', body)
        body = PLAIN_TEXT_PATTERN.sub(' ', body)
        body = SPACES_PATTERN.sub(' ', body)
        body = bytes(body, "utf-8").decode("unicode_escape")
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
        return flags[0].replace("\\\\", "\\").split(", ") if flags and flags[0] else []
    
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
        header_match = HEADERS_PATTERN.search(message, re.DOTALL)
        if not header_match:
            return None
            
        sender = date = subject = receiver = ""            
        header_match = header_match.group()
            
        # From / Sender
        sender = SENDER_PATTERN.search(header_match, re.DOTALL)
        sender = sender.group(1) if sender else ""
            
        # Date
        date = DATE_PATTERN.search(header_match, re.DOTALL)
        date = date.group(1) if date else ""

        # To / Receiver
        receiver = RECEIVER_PATTERN.search(header_match, re.DOTALL)
        receiver = receiver.group(1) if receiver else ""

        # Subject
        subject = SUBJECT_PATTERN.search(header_match, re.DOTALL)
        subject = subject.group(1) if subject else ""
        if subject.startswith('=?utf-8'):
            subject = email.header.decode_header(subject)[0][0].decode('utf-8')
            
        return {
            "sender": sender,
            "date": date,
            "receiver": receiver,
            "subject": subject
        }
    
__all__ = ["MessageParser", "MessageHeaders"]