import os
import jwt
from dotenv import load_dotenv

if not load_dotenv():
    print("loading .env failed")

def authenticate(token: str) -> None:
    payload = jwt.decode(
        token, 
        os.environ["BETTER_AUTH_SECRET"]
    )
    return payload

