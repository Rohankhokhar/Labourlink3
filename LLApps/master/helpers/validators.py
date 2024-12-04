import re

def is_valid_email(email):
    """
    Validate an email address and provide feedback.

    Args:
        email (str): The email address to validate.

    Returns:
        tuple: (bool, str) where the first element is True if valid, False otherwise,
               and the second element is a message explaining the result.
    """
    if not isinstance(email, str):
        return False, "Email must be a string."

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(email_regex, email):
        return True, "Valid email address."
    else:
        return False, "Invalid email address. Ensure it follows the format: username@domain.com."


def is_valid_mobile_number(mobile_number):
    """
    Validate a mobile number and provide feedback.

    Args:
        mobile_number (str): The mobile number to validate.

    Returns:
        tuple: (bool, str) where the first element is True if valid, False otherwise,
               and the second element is a message explaining the result.
    """
    if not isinstance(mobile_number, str):
        return False, "Mobile number must be a string."

    general_mobile_regex = r'^\d{10}$'

    if re.match(general_mobile_regex, mobile_number):
        return True, "Valid mobile number."
    else:
        return False, (
            "Invalid mobile number. Ensure it contains only digits, "
            "starts with a non-zero digit, and is up to 15 characters long."
        )


def is_valid_password(password):
    """
    Validate a password and provide feedback.

    Args:
        password (str): The password to validate.

    Returns:
        tuple: (bool, str) where the first element is True if valid, False otherwise,
               and the second element is a message explaining the result.
    """
    if not isinstance(password, str):
        return False, "Password must be a string."

    password_regex = (
        r'^(?=.*[a-z])'        # At least one lowercase letter
        r'(?=.*[A-Z])'         # At least one uppercase letter
        r'(?=.*\d)'            # At least one digit
        r'(?=.*[@$!%*?&])'     # At least one special character
        r'[A-Za-z\d@$!%*?&]{8,32}$'  # Length between 8 to 32 characters
    )

    if re.match(password_regex, password):
        return True, "Valid password."
    else:
        return False, (
            "Invalid password. Ensure it has at least one uppercase letter, "
            "one lowercase letter, one digit, one special character, "
            "and is between 8 to 32 characters long."
        )