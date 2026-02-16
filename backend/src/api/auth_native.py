"""
FastAPI-native authentication system
Replaces better-auth with a pure Python implementation
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select

import db
from tables import Account, Session as DBSession, User

# Load environment variables
if not load_dotenv():
    print("Warning: .env file not loaded")

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Request/Response Models
class LoginRequest(BaseModel):
    email: str
    password: str


class SignUpRequest(BaseModel):
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    emailVerified: bool
    image: str | None = None


class SessionResponse(BaseModel):
    user: UserResponse | None
    session: dict | None


# Helper Functions
def hash_password(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    """Create a JWT access token"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_db(session: Session, email: str) -> tuple[User, Account] | None:
    """Get user and their email/password account from database"""
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return None

    account = session.exec(
        select(Account).where(
            Account.userId == user.id,
            Account.providerId == "credential",  # Email/password provider
        )
    ).first()

    if not account:
        return None

    return user, account


def create_session_in_db(
    session: Session, user_id: str, token: str, request: Request
) -> DBSession:
    """Create a new session in the database"""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    db_session = DBSession(
        id=secrets.token_urlsafe(16),
        userId=user_id,
        token=token,
        expiresAt=expires_at,
        ipAddress=request.client.host if request.client else None,
        userAgent=request.headers.get("user-agent"),
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
    )

    session.add(db_session)
    session.commit()
    session.refresh(db_session)

    return db_session


def get_current_user(
    session: Annotated[Session, Depends(db.get_session)],
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> User | None:
    """Get the current authenticated user from JWT token"""
    if not access_token:
        return None

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except jwt.InvalidTokenError:
        return None

    user = session.get(User, user_id)
    return user


def require_auth(
    current_user: Annotated[User | None, Depends(get_current_user)],
) -> User:
    """Require authentication - raises 401 if not authenticated"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return current_user


# Auth endpoints
async def login(
    request: Request,
    login_data: LoginRequest,
    response: Response,
    session: Session = Depends(db.get_session),
) -> SessionResponse:
    """Login with email and password"""
    result = get_user_from_db(session, login_data.email)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user, account = result

    # Verify password
    if not account.password or not verify_password(
        login_data.password, account.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token
    access_token = create_access_token(user.id)

    # Create session in database
    db_session = create_session_in_db(session, user.id, access_token, request)

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Only send over HTTPS
        samesite="none",  # Required for cross-origin (Netlify -> Backend)
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return SessionResponse(
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            emailVerified=user.emailVerified,
            image=user.image,
        ),
        session={"token": access_token, "expiresAt": db_session.expiresAt.isoformat()},
    )


async def logout(
    response: Response,
    session: Session = Depends(db.get_session),
    access_token: str | None = Cookie(None),
) -> dict:
    """Logout - delete session and clear cookie"""
    if access_token:
        # Delete session from database
        db_session = session.exec(
            select(DBSession).where(DBSession.token == access_token)
        ).first()
        if db_session:
            session.delete(db_session)
            session.commit()

    # Clear cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="none",
    )

    return {"message": "Logged out successfully"}


async def get_session(
    current_user: Annotated[User | None, Depends(get_current_user)],
) -> SessionResponse:
    """Get current session information"""
    if not current_user:
        return SessionResponse(user=None, session=None)

    return SessionResponse(
        user=UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            emailVerified=current_user.emailVerified,
            image=current_user.image,
        ),
        session={"user_id": current_user.id},
    )


async def sign_up(
    request: Request,
    signup_data: SignUpRequest,
    response: Response,
    session: Session = Depends(db.get_session),
) -> SessionResponse:
    """Sign up a new user (optional - you said you don't need this from frontend)"""
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == signup_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user
    user = User(
        id=secrets.token_urlsafe(16),
        name=signup_data.name,
        email=signup_data.email,
        emailVerified=False,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
    )
    session.add(user)

    # Create email/password account
    account = Account(
        id=secrets.token_urlsafe(16),
        accountId=signup_data.email,
        providerId="credential",
        userId=user.id,
        password=hash_password(signup_data.password),
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
    )
    session.add(account)
    session.commit()

    # Auto-login after signup
    access_token = create_access_token(user.id)
    db_session = create_session_in_db(session, user.id, access_token, request)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return SessionResponse(
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            emailVerified=user.emailVerified,
            image=user.image,
        ),
        session={"token": access_token, "expiresAt": db_session.expiresAt.isoformat()},
    )
