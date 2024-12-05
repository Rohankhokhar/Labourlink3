import random
import string

def generate_otp(length=6):
    """
    Generates a secure One-Time Password (OTP) consisting of random digits.

    Parameters:
    ----------
    length : int, optional
        The length of the OTP to be generated. Default is 6.

    Returns:
    -------
    str
        A string representing the generated OTP.
    
    Raises:
    ------
    ValueError
        If the length is less than 4 or greater than 10.
    
    Examples:
    --------
    >>> generate_otp()
    '724351'
    
    >>> generate_otp(4)
    '8293'

    >>> generate_otp(8)
    '39472918'
    """
    
    if length < 4 or length > 10:
        raise ValueError("OTP length should be between 4 and 10.")
    
    otp = ''.join(random.choices(string.digits, k=length))
    return otp