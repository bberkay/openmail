"""
This module contains the types used in the OpenMail module.
"""
from __future__ import annotations
from enum import Enum
from typing import Optional, Sequence, Tuple
from dataclasses import dataclass, field, fields
import json

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
    smaller_than: Optional[int] = 0
    larger_than: Optional[int] = 0
    include: Optional[str] = ""
    exclude: Optional[str] = ""
    included_flags: Optional[list[str]] = field(default_factory=list)
    has_attachments: Optional[bool] = False

    def __str__(self) -> str:
        """Returns a string representation of the SearchCriteria object."""
        return str(self.__dict__)

    @classmethod
    def parse_raw(cls, raw: str) -> SearchCriteria | str:
        """Parses a string representation of a SearchCriteria object."""
        if not raw:
            return ""

        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                return raw
            return SearchCriteria(**data)
        except json.JSONDecodeError:
            return raw

@dataclass
class BasicEmail():
    """Represents a basic email."""
    uid: str
    sender: str | Tuple[str, str]
    receiver: str
    date: str
    subject: str
    body: str
    flags: Optional[list[str]] = field(default_factory=list)
    attachments: Optional[list[Attachment]] = field(default_factory=list)

@dataclass
class CompleteEmail(BasicEmail):
    """Represents an email with its content."""
    cc: Optional[str] = ""
    bcc: Optional[str] = ""
    message_id: Optional[str] = ""
    metadata: Optional[dict] = field(default_factory=dict)

    def __getitem__(self, item):
        """Allows dictionary-like access to dataclass attributes."""
        return getattr(self, item)

    def keys(self):
        """Returns a list of all field names in the dataclass instance."""
        return [field.name for field in fields(self)]

@dataclass
class DraftEmail():
    """
    Represents an email to be sent/replied/forwarded.
    If the email is being replied or forwarded, the
    `uid` field must be provided.
    """
    sender: str | Tuple[str, str]
    receiver: str | list[str]
    #date: str
    subject: str
    body: str
    uid: Optional[str] = ""
    cc: Optional[str | list[str]] = ""
    bcc: Optional[str | list[str]] = ""
    metadata: Optional[dict] = field(default_factory=dict)
    attachments: Optional[list[Attachment]] = field(default_factory=list)
    mail_options: Optional[Sequence[str]] = field(default_factory=list)
    rcpt_options: Optional[Sequence[str]] = field(default_factory=list)

    def __getitem__(self, item):
        """Allows dictionary-like access to dataclass attributes."""
        return getattr(self, item)

    def keys(self):
        """Returns a list of all field names in the dataclass instance."""
        return [field.name for field in fields(self)]

@dataclass
class Mailbox():
    """Represents the mailbox's contents."""
    folder: str
    emails: list[BasicEmail]
    total: int

@dataclass
class Flags():
    """Represents an email's flags."""
    uid: str
    flags: list[str]

@dataclass
class Attachment():
    """Represents an email attachment."""
    path: Optional[str] = None
    name: Optional[str] = None
    size: Optional[int] = None
    type: Optional[str] = None
    data: Optional[str] = None
    cid: Optional[str] = None

    def keys(self):
        """Returns a list of all field names in the dataclass instance."""
        return [field.name for field in fields(self)]


"""
Enums
"""
class Mark(str, Enum):
    """
    Standard email marks.

    References:
        - https://datatracker.ietf.org/doc/html/rfc9051#name-flags-message-attribute
    """
    Flagged = "\\Flagged"
    Seen = "\\Seen"
    Answered = "\\Answered"
    Draft = "\\Draft"
    Deleted = "\\Deleted"
    Unflagged = "\\Unflagged"
    Unseen = "\\Unseen"
    Unanswered = "\\Unanswered"
    Undraft = "\\Undraft"
    Undeleted = "\\Undeleted"

    def __str__(self):
        return self.value


class Folder(str, Enum):
    """
    Standard email folders.

    References:
        - https://datatracker.ietf.org/doc/html/rfc6154#autoid-3
    """
    Inbox = 'Inbox'
    All = 'All'
    Archive = 'Archive'
    Drafts = 'Drafts'
    Flagged = 'Flagged'
    Junk = 'Junk'
    Sent = 'Sent'
    Trash = 'Trash'
    Important = 'Important'

    def __str__(self):
        return self.value

__all__ = [
    "SearchCriteria",
    "BasicEmail",
    "Attachment",
    "CompleteEmail",
    "DraftEmail",
    "Mailbox",
    "Flags",
    "Folder",
    "Mark"
]
