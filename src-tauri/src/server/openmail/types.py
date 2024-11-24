"""
This module contains the types used in the OpenMail module.
"""
from typing import List, Optional, Sequence, Tuple
from dataclasses import dataclass, field

@dataclass
class SearchCriteria():
    """
    A class that represents IMAP search criteria as a dataclass.
    https://datatracker.ietf.org/doc/html/rfc9051#name-search-command
    """
    senders: Optional[List[str]] = field(default_factory=list)
    receivers: Optional[List[str]] = field(default_factory=list)
    subject: Optional[str] = ""
    since: Optional[str] = ""
    before: Optional[str] = ""
    flags: Optional[List[str]] = field(default_factory=list)
    include: Optional[str] = ""
    exclude: Optional[str] = ""
    has_attachments: Optional[bool] = False

@dataclass
class EmailSummary():
    """
    A class that represents an email summary as a dataclass.
    """
    uid: str
    sender: str | Tuple[str, str] 
    receiver: str
    date: str
    subject: str
    body_short: str
    flags: Optional[List[str]] = field(default_factory=list)

@dataclass
class Attachment():
    """
    A class that represents an email attachment as a dataclass.
    """
    cid: str
    name: str
    data: str
    size: str
    type: str

@dataclass
class EmailWithContent():
    """
    A class that represents an email with its content as a dataclass.
    """
    uid: str
    sender: str | Tuple[str, str] 
    receiver: str
    date: str
    subject: str
    body: str
    message_id: Optional[str] = ""
    flags: Optional[List[str]] = field(default_factory=list)    
    cc: Optional[str] = ""
    bcc: Optional[str] = ""
    metadata: Optional[dict] = field(default_factory=dict)
    attachments: Optional[List[Attachment]] = field(default_factory=list)

@dataclass
class EmailToSend():
    """
    A class that represents an email to be sent/replied/forwarded as 
    a dataclass. If the email is being replied or forwarded, the
    `uid` field must be provided.
    """
    sender: str | Tuple[str, str] 
    receiver: str
    #date: str
    subject: str
    body: str    
    uid: Optional[str] = ""
    cc: Optional[str] = ""
    bcc: Optional[str] = ""
    metadata: Optional[dict] = field(default_factory=dict)
    attachments: Optional[List[Attachment]] = field(default_factory=list)
    mail_options: Optional[Sequence[str]] = field(default_factory=list)
    rcpt_options: Optional[Sequence[str]] = field(default_factory=list)

@dataclass
class Mailbox():
    """
    A class that represents the mailbox's contents as a dataclass.
    """
    folder: str
    emails: List[EmailSummary]
    total: int

__all__ = [
    "SearchCriteria", 
    "Attachment", 
    "EmailSummary", 
    "EmailWithContent", 
    "EmailToSend", 
    "Mailbox", 
]