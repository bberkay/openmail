"""
This module contains the types used in the OpenMail module.
"""
from typing import List, Optional, Sequence, Tuple
from dataclasses import dataclass, field

@dataclass
class SearchCriteria():
    """
    Represents IMAP search criteria.

    References:
        - https://datatracker.ietf.org/doc/html/rfc9051#name-search-command
    """
    senders: Optional[List[str]] = field(default_factory=list)
    receivers: Optional[List[str]] = field(default_factory=list)
    cc: Optional[List[str]] = field(default_factory=list)
    bcc: Optional[List[str]] = field(default_factory=list)
    subject: Optional[str] = ""
    since: Optional[str] = ""
    before: Optional[str] = ""
    included_flags: Optional[List[str]] = field(default_factory=list)
    excluded_flags: Optional[List[str]] = field(default_factory=list)
    smaller_than: Optional[int] = 0
    larger_than: Optional[int] = 0
    include: Optional[str] = ""
    exclude: Optional[str] = ""
    has_attachments: Optional[bool] = False

    def __str__(self) -> str:
        """Returns a string representation of the SearchCriteria object."""
        return str(self.__dict__)

@dataclass
class EmailSummary():
    """Represents an email summary."""
    uid: str
    sender: str | Tuple[str, str]
    receiver: str
    date: str
    subject: str
    body_short: str
    flags: Optional[List[str]] = field(default_factory=list)
    attachments: Optional[List[str]] = field(default_factory=list)

@dataclass
class Attachment():
    """Represents an email attachment."""
    name: str
    data: str
    size: str
    type: str
    cid: str | None = None

@dataclass
class EmailWithContent():
    """Represents an email with its content."""
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
    Represents an email to be sent/replied/forwarded.
    If the email is being replied or forwarded, the
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

    def __str__(self) -> str:
        """Returns a string representation of the EmailToSend object."""
        return str(self.__dict__)

@dataclass
class Mailbox():
    """Represents the mailbox's contents."""
    folder: str
    emails: List[EmailSummary]
    total: int

@dataclass
class Flags():
    """Represents an email's flags."""
    uid: str
    flags: List[str]

__all__ = [
    "SearchCriteria",
    "Attachment",
    "EmailSummary",
    "EmailWithContent",
    "EmailToSend",
    "Mailbox",
]
