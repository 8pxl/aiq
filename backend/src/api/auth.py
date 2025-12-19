import base64
from dataclasses import dataclass
import os
from typing import TypedDict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import jwt
from dotenv import load_dotenv
import requests

class Jwk(TypedDict):
    crv: str
    x: str
    kty: str
    kid: str

if not load_dotenv():
    print("loading .env failed")

def base64url_decode(s: str):
    rem = len(s) % 4
    if rem > 0:
        s+= '=' * (4 - rem)
    return base64.urlsafe_b64decode(s)

def authenticate(token: str) -> None:
    jwks_endpoint = f"{os.environ["BETTER_AUTH_URL"]}/api/auth/jwks"
    jwks = requests.get(jwks_endpoint)
    if jwks:
        keys: list[Jwk] = jwks.json()["keys"]
        assert(len(keys) == 1)
        key: str = keys[0]["x"]
        public_key_bytes = base64url_decode(key)
        public_key_obj = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key_pem = public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        payload = jwt.decode(
            token, 
            public_key_pem,
            audience=os.environ["BETTER_AUTH_URL"],
            algorithms= ["EdDSA"]
        )
        return payload

