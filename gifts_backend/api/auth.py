import time
import jwt
from flask import session
key = "CrazySecretString"
algorithm = "HS256"
tokenLifeTimeSeconds = 60 * 60 * 24 * 3
issuer = "theIssuerOfTheToken"


def login(authentication):
    email, password = authentication.values()
    # check if credentials are correct
    timestamp = int(time.time())
    payload = {
        "active": True,
        "iss": issuer,
        "iat": timestamp,
        "exp": timestamp + tokenLifeTimeSeconds,
        "sub": email,
        "username": email
    }
    return jwt.encode(payload, key, algorithm=algorithm)


def decode_token(token):
    return jwt.decode(token, key, issuer=issuer, algorithms=algorithm)
