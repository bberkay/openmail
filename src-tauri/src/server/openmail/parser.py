"""

"""
import re
import email
from typing import TypedDict

# Custom types
class MessageHeaders(TypedDict):
    """
    
    """
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
FLAGS_PATTERN = re.compile(r'FLAGS \((.*?)\)')
LINE_PATTERN = re.compile(r'\\.*?r\\.*?n')
PLAIN_TEXT_PATTERN = re.compile(r'=[A-Za-z0-9]+|\(.*?\)|\*+|-+|\s+')
SPACES_PATTERN = re.compile(r'\s+')

class MessageParser:
    """
    """

    @staticmethod
    def messages(message: str) -> list[str]:
        """
        
        """
        return re.findall(MESSAGE_PATTERN, message)

    @staticmethod
    def body_from_message(message: str) -> str:
        """
        
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
        
        """
        return ATTACHMENT_PATTERN.findall(message)
    
    @staticmethod
    def flags_from_message(message: str) -> list[str]:
        """

        """
        flags = FLAGS_PATTERN.findall(message)
        return flags[0].replace("\\\\", "\\").split(", ") if flags and flags[0] else []
    
    @staticmethod
    def headers_from_message(message: str) -> MessageHeaders:
        """
        
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