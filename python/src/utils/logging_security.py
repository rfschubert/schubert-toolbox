"""
Logging Security Utilities.

This module provides utilities for secure logging to prevent log injection attacks
and other security vulnerabilities in log messages.

Following the code quality rules:
- prevent-log-injection (HIGH severity)
- input-validation-logging (HIGH severity)
"""

import re
from typing import Any


def sanitize_for_logging(value: Any, max_length: int = 100) -> str:
    """
    Sanitize value for safe logging to prevent log injection attacks.

    This function removes control characters, newlines, and other potentially
    dangerous characters that could be used for log injection attacks.

    Args:
        value: Value to sanitize (will be converted to string)
        max_length: Maximum length to truncate to (default: 100)

    Returns:
        Sanitized string safe for logging

    Examples:
        >>> sanitize_for_logging("88304053")
        "88304053"

        >>> sanitize_for_logging("88304053\\nCRITICAL: Fake log")
        "88304053\\\\nCRITICAL: Fake log"

        >>> sanitize_for_logging(None)
        "None"
    """
    if value is None:
        return "None"

    # Convert to string and limit length
    safe_value = str(value)[:max_length]

    # Remove control characters and other dangerous characters
    # This includes characters 0x00-0x1f (control chars) and 0x7f-0x9f (extended control)
    safe_value = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", safe_value)

    # Replace newlines and carriage returns with escaped versions
    safe_value = safe_value.replace("\n", "\\n").replace("\r", "\\r")

    # Replace tab characters with escaped version
    safe_value = safe_value.replace("\t", "\\t")

    return safe_value


def sanitize_cache_key(cache_key: str, max_length: int = 50) -> str:
    """
    Sanitize cache key for safe logging.

    Cache keys often contain user input (like postal codes) and need
    special handling for logging.

    Args:
        cache_key: Cache key to sanitize
        max_length: Maximum length to truncate to (default: 50)

    Returns:
        Sanitized cache key safe for logging
    """
    return sanitize_for_logging(cache_key, max_length)


def sanitize_user_input(user_input: Any, max_length: int = 20) -> str:
    """
    Sanitize user input for safe logging.

    User inputs like postal codes, values to format, etc. should be
    sanitized before being logged.

    Args:
        user_input: User input to sanitize
        max_length: Maximum length to truncate to (default: 20)

    Returns:
        Sanitized user input safe for logging
    """
    return sanitize_for_logging(user_input, max_length)


def sanitize_error_message(error: Exception, max_length: int = 200) -> str:
    """
    Sanitize error message for safe logging.

    Error messages might contain user input or other sensitive information
    that needs to be sanitized.

    Args:
        error: Exception object
        max_length: Maximum length to truncate to (default: 200)

    Returns:
        Sanitized error message safe for logging
    """
    return sanitize_for_logging(str(error), max_length)


def create_safe_log_context(**kwargs) -> dict:
    """
    Create a safe logging context by sanitizing all values.

    This function takes keyword arguments and returns a dictionary
    with all values sanitized for safe logging.

    Args:
        **kwargs: Key-value pairs to sanitize

    Returns:
        Dictionary with sanitized values

    Example:
        >>> context = create_safe_log_context(
        ...     postal_code="88304053\\nFAKE",
        ...     driver="viacep",
        ...     user_id=12345
        ... )
        >>> context
        {'postal_code': '88304053\\\\nFAKE', 'driver': 'viacep', 'user_id': '12345'}
    """
    safe_context = {}

    for key, value in kwargs.items():
        safe_context[key] = sanitize_for_logging(value)

    return safe_context
