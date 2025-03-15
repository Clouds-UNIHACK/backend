import re


def is_valid_email(email: str) -> bool:
    """
    Check if the email is valid.
    """
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))
