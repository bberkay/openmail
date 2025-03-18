"""
Utility functions to be used in other modules of OpenMail.

These functions provide helper methods for email-related operations,
including domain extraction, date conversion, and other utility tasks.
"""

from datetime import datetime
from typing import Iterable

def extract_username(email: str) -> str:
    """Extract the user name from an email address."""
    return (email.split("@")[0].split("<")[1] if "<" in email else email.split('@')[0]).strip()

def extract_domain(email: str, full: bool = False) -> str:
    """Extract the domain name from an email address."""
    return (email.split('@')[1].split(".")[0] if not full else email.split('@')[1]).strip()

def extract_fullname(sender: str) -> str:
    """Extract the fullname from given sender info."""
    return (sender.split("<")[0] if "<" in sender and "@" in sender else "").strip()

def extract_email_address(sender: str) -> str:
    """Extract the email address from a full name <email@address> string"""
    return (sender.split("<")[1].replace(">", "") if "<" in sender else sender if "@" in sender else "").strip()

def extract_email_addresses(senders: Iterable[str]) -> list[str]:
    """Extract and remove nullish email addressses from senders."""
    return list(filter(lambda x: bool(x) is not None, map(extract_email_address, senders)))

def truncate_text(content: str, max_length: int) -> str:
    """Truncate text to a specified maximum length."""
    return (content[:max_length] + "...") if len(content) > max_length else content

def choose_positive(var1: int, var2: int) -> int:
    """Select the first positive number from two input integers."""
    return var1 if var1 > 0 else var2

def contains_non_ascii(string: str) -> bool:
    """Check if a string contains any non-ASCII characters."""
    return any(ord(char) > 127 for char in string)

def tuple_to_sender_string(sender: tuple[str, str] | str) -> str:
    """Formats the sender's name and email into a single string."""
    return sender[0] + f"<{sender[1]}>" if not isinstance(sender, str) else sender

def add_quotes_if_str(value: str) -> str:
    """Add quotes to variables if it is string ant will be trimmed."""
    return f'"{value.strip()}"' if isinstance(value, str) else value

def convert_to_imap_date(date: str | datetime) -> str:
    """Format datetime date or string date to IMAP4 date format."""
    return datetime.fromisoformat(date).strftime('%d-%b-%Y') if isinstance(date, str) else date.strftime('%d-%b-%Y')
