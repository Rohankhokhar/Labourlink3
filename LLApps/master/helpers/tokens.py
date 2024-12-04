from django.conf import settings

import jwt
import datetime


def create_jwt_token(labour_id):
    """
    Generate a JSON Web Token (JWT) for a given labour ID.

    This function creates a JWT containing the labour ID, an issued-at time (iat),
    and an expiration time (exp) set to 30 minutes from the current time.

    Args:
        labour_id (str or int): The unique identifier of the labour user.

    Returns:
        str: A JWT token encoded with the provided payload and signed using the HS256 algorithm.

    Raises:
        ValueError: If the `labour_id` is not provided.

    Example:
        token = create_jwt_token(12345)
        print(token)
    """
    if not labour_id:
        return ValueError("Labour must be provided")
    
    payload = {
        "labour_id": labour_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def verify_jwt_token(token):
    """
    Verify and decode a JSON Web Token (JWT).

    This function decodes a JWT using the secret key and verifies its validity.
    It returns the decoded payload if the token is valid. If the token has expired
    or is invalid, it returns an appropriate error message.

    Args:
        token (str): The JWT token to be verified.

    Returns:
        dict: The decoded payload if the token is valid.
              If the token is invalid or expired, returns a dictionary with an error message.

    Exceptions:
        jwt.ExpiredSignatureError: Raised when the token has expired.
        jwt.InvalidTokenError: Raised when the token is invalid.

    Example:
        payload = verify_jwt_token(token)
        if 'error' in payload:
            print(payload['error'])
        else:
            print("Token is valid:", payload)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print(f"Decoded payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return {"error": "Token has expired."}
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return {"error": "Invalid token."}