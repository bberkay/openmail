"""
Utility functions to be used in other modules of OpenMail.

These functions provide helper methods for email-related operations,
including domain extraction, date conversion, and other utility tasks.
"""
from datetime import datetime

def extract_domain(email: str) -> str:
    """
    Extract the domain name from an email address.

    Args:
        email (str): A valid email address

    Returns:
        str: The domain name without the TLD (top-level domain)

    Example:
        >>> extract_domain('hGjwF@example.com')
        'example'
    """
    return email.split('@')[1].split(".")[0]

def convert_to_imap_date(date: str) -> str:
    """
    Convert a date to IMAP-compatible format as specified in RFC 5322.

    Transforms a date from 'YYYY-MM-DD' to the IMAP standard 'DD-MMM-YYYY' format.

    Args:
        date (str): Date string in 'YYYY-MM-DD' format

    Returns:
        str: Date formatted as 'DD-MMM-YYYY'

    References:
        https://datatracker.ietf.org/doc/html/rfc5322#section-3.3

    Example:
        >>> convert_to_imap_date('2022-01-01')
        '01-Jan-2022'
    """
    return datetime.strptime(date, '%Y-%m-%d').strftime('%d-%b-%Y')

def convert_date_to_iso(date: str) -> str:
    """
    Convert email date string to ISO 8601 format.

    Converts an email date string (RFC 2822 format) to a standardized
    datetime string in 'YYYY-MM-DD HH:MM:SS' format.

    Args:
        date (str): Email date string in format like 'Wed, 15 Nov 2023 14:30:00 +0000'

    Returns:
        str: Formatted date string in 'YYYY-MM-DD HH:MM:SS' format

    Example:
        >>> convert_date_to_iso('Wed, 15 Nov 2023 14:30:00 +0000')
        '2023-11-15 14:30:00'
    """
    return datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(content: str, max_length: int) -> str:
    """
    Truncate text to a specified maximum length.

    Args:
        content (str): Input text to truncate
        max_length (int): Maximum allowed text length

    Returns:
        str: Truncated text or original content

    Example:
        >>> truncate_text("Hello world", 5)
        'Hello...'

        >>> truncate_text("Short", 10)
        'Short'
    """
    if len(content) > max_length:
        return content[:max_length] + "..."

    return content

def choose_positive(var1: int, var2: int) -> int:
    """
    Select the first positive number from two input integers.

    Args:
        var1 (int): First integer to evaluate
        var2 (int): Second integer to evaluate

    Returns:
        int: The first positive number. If both are non-positive, returns var2.

    Example:
        >>> choose_positive(-1, 2)
        2

        >>> choose_positive(1, 2)
        1
    """
    return var1 if var1 > 0 else var2

def contains_non_ascii(string: str) -> bool:
    """
    Check if a string contains any non-ASCII characters.

    Args:
        string (str): Input string to check

    Returns:
        bool: True if string contains non-ASCII characters, False otherwise
    """
    return any(ord(char) > 127 for char in string)

def make_size_human_readable(size: int | None) -> str:
    """
    Convert a file size in bytes to a human-readable format.

    Args:
        size (int | None): Size in bytes, or None

    Returns:
        str: Formatted file size with appropriate unit (B, KB, MB, or GB)

    Example:
        >>> make_size_human_readable(1536)
        '1.50 KB'
    """
    if size is None:
        return "0 B"
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / 1024 / 1024:.2f} MB"
    else:
        return f"{size / 1024 / 1024 / 1024:.2f} GB"
