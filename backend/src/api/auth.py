import base64
from dataclasses import dataclass
import os
from typing import TypedDict, cast
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import Depends, HTTPException, Header, status
import jwt
from dotenv import load_dotenv
import requests
from sqlmodel import Session
import db

class Jwk(TypedDict):
    crv: str
    x: str
    kty: str
    kid: str

class JwtClaim(TypedDict):
    iat: str
    name: str
    email: str
    emailVerified: str
    image: str
    createdAt: str
    updatedAt: str
    id: str
    sub: str
    exp: int
    iss: str
    aud: str

if not load_dotenv():
    print("loading .env failed")

def base64url_decode(s: str):
    rem = len(s) % 4
    if rem > 0:
        s+= '=' * (4 - rem)
    return base64.urlsafe_b64decode(s)

def authenticate(session: Session, token: str) -> bool:
    jwks_endpoint = f"{os.environ["BETTER_AUTH_URL"]}/api/auth/jwks"
    jwks = requests.get(jwks_endpoint)
    if not jwks:
        return False

    keys = cast(list[Jwk], jwks.json()["keys"])

    # docs didn't really say if there could be more than one keys so ill handle it when i see it
    # FIGURE this out before pushing to prod
    if (len(keys) != 1):
        print("expected length of keys to be 1!!")
    assert(len(keys) == 1)

    key: str = keys[0]["x"]
    public_key_bytes = base64url_decode(key)
    public_key_obj = Ed25519PublicKey.from_public_bytes(public_key_bytes)
    public_key_pem = public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    payload  = cast(JwtClaim, jwt.decode(
        token, 
        public_key_pem,
        audience=os.environ["BETTER_AUTH_URL"],
        algorithms= ["EdDSA"]
    ))

    if not payload:
        return False

    valid = 0b1

    valid |= db.user_has_perms(session, payload["id"])
    valid |= payload["iss"] == os.environ["BETTER_AUTH_URL"]

    return bool(valid)


def authenticate_user(session: Session = Depends(db.get_session),
                     authorization: str | None = Header(),):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Authorization header")
    _, _, token = authorization.partition(" ")
    if not authenticate(session, token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
