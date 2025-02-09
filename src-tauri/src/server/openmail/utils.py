"""
Utility functions to be used in other modules of OpenMail.

These functions provide helper methods for email-related operations,
including domain extraction, date conversion, and other utility tasks.
"""

def extract_username(email: str) -> str:
    """Extract the user name from an email address."""
    return email.split('@')[0]

def extract_domain(email: str) -> str:
    """Extract the domain name from an email address."""
    return email.split('@')[1].split(".")[0]

def truncate_text(content: str, max_length: int) -> str:
    """Truncate text to a specified maximum length."""
    return (content[:max_length] + "...") if len(content) > max_length else content

def choose_positive(var1: int, var2: int) -> int:
    """Select the first positive number from two input integers."""
    return var1 if var1 > 0 else var2

def contains_non_ascii(string: str) -> bool:
    """Check if a string contains any non-ASCII characters."""
    return any(ord(char) > 127 for char in string)

def add_quotes_if_str(value: str):
    """Add quotes to variables if it is string ant will be trimmed."""
    return f'"{value.strip()}"' if isinstance(value, str) else value
