from django.conf import settings

import jwt
import datetime


def create_jwt_token(labour_id):
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