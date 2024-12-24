"""
Utility functions to be used in other modules of OpenMail.

These functions provide helper methods for email-related operations,
including domain extraction, date conversion, and other utility tasks.
"""

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
