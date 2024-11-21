"""
This module contains the types used in the OpenMail module.
"""
from typing import List, Optional
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

class LoginException(Exception):
    """
    An exception raised when there is an issue with the login process.
    """
