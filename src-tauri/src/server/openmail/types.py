"""
This module contains the types used in the OpenMail module.
"""
from __future__ import annotations
from typing import Optional, Sequence, Tuple
from dataclasses import dataclass, field

@dataclass
class SearchCriteria():
    """
    Represents IMAP search criteria.

    References:
        - https://datatracker.ietf.org/doc/html/rfc9051#name-search-command
    """
    senders: Optional[list[str]] = field(default_factory=list)
    receivers: Optional[list[str]] = field(default_factory=list)
    cc: Optional[list[str]] = field(default_factory=list)
    bcc: Optional[list[str]] = field(default_factory=list)
    subject: Optional[str] = ""
    since: Optional[str] = ""
    before: Optional[str] = ""
    included_flags: Optional[list[str]] = field(default_factory=list)
    excluded_flags: Optional[list[str]] = field(default_factory=list)
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
    flags: Optional[list[str]] = field(default_factory=list)
    attachments: Optional[list[Attachment]] = field(default_factory=list)

@dataclass
class Attachment():
    """Represents an email attachment."""
    path: Optional[str] = None
    name: Optional[str] = None
    size: Optional[int] = None
    data: Optional[str] = None
    type: Optional[str] = None
    cid: Optional[str] = None

@dataclass
class EmailWithContent():
    """Represents an email with its content."""
    uid: str
    sender: str | Tuple[str, str]
    receiver: str
    date: str
    subject: str
    body: str
    cc: Optional[str] = ""
    bcc: Optional[str] = ""
    flags: Optional[list[str]] = field(default_factory=list)
    attachments: Optional[list[Attachment]] = field(default_factory=list)
    message_id: Optional[str] = ""
    metadata: Optional[dict] = field(default_factory=dict)

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
    attachments: Optional[list[Attachment]] = field(default_factory=list)
    mail_options: Optional[Sequence[str]] = field(default_factory=list)
    rcpt_options: Optional[Sequence[str]] = field(default_factory=list)

    def __str__(self) -> str:
        """Returns a string representation of the EmailToSend object."""
        return str(self.__dict__)

@dataclass
class Mailbox():
    """Represents the mailbox's contents."""
    folder: str
    emails: list[EmailSummary]
    total: int

@dataclass
class Flags():
    """Represents an email's flags."""
    uid: str
    flags: list[str]

__all__ = [
    "SearchCriteria",
    "EmailSummary",
    "Attachment",
    "EmailWithContent",
    "EmailToSend",
    "Mailbox",
    "Flags"
]
