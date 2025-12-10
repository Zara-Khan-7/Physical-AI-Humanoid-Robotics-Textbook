"""Authentication routes for user signup/signin."""

import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field, EmailStr

router = APIRouter()

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "users.db"


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            software_experience TEXT DEFAULT 'beginner',
            hardware_experience TEXT DEFAULT 'beginner',
            learning_goals TEXT DEFAULT ''
        )
    """)

    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


# Initialize database on module load
init_db()


def hash_password(password: str) -> str:
    """Hash a password with salt."""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hash_obj.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against stored hash."""
    try:
        salt, hash_hex = stored_hash.split(':')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == hash_hex
    except Exception:
        return False


def create_session(user_id: int) -> str:
    """Create a new session token for a user."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user_id, token, expires_at)
    )
    conn.commit()
    conn.close()

    return token


def get_user_from_token(token: str) -> Optional[dict]:
    """Get user from session token."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, u.email, u.name, u.software_experience, u.hardware_experience, u.learning_goals
        FROM users u
        JOIN sessions s ON u.id = s.user_id
        WHERE s.token = ? AND s.expires_at > ?
    """, (token, datetime.utcnow()))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


# Request/Response Models
class SignUpRequest(BaseModel):
    """Sign up request body."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)
    software_experience: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    hardware_experience: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    learning_goals: str = Field(default="", max_length=500)


class SignInRequest(BaseModel):
    """Sign in request body."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User data response."""
    id: int
    email: str
    name: str
    software_experience: str
    hardware_experience: str
    learning_goals: str


class AuthResponse(BaseModel):
    """Authentication response."""
    user: UserResponse
    token: str


class UpdateProfileRequest(BaseModel):
    """Update profile request."""
    name: Optional[str] = None
    software_experience: Optional[str] = Field(default=None, pattern="^(beginner|intermediate|advanced)$")
    hardware_experience: Optional[str] = Field(default=None, pattern="^(beginner|intermediate|advanced)$")
    learning_goals: Optional[str] = Field(default=None, max_length=500)


# Dependency for protected routes
async def get_current_user(authorization: str = Header(None)) -> dict:
    """Get current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user


@router.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """Create a new user account."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    password_hash = hash_password(request.password)
    cursor.execute("""
        INSERT INTO users (email, password_hash, name, software_experience, hardware_experience, learning_goals)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (request.email, password_hash, request.name, request.software_experience,
          request.hardware_experience, request.learning_goals))

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Create session
    token = create_session(user_id)

    return AuthResponse(
        user=UserResponse(
            id=user_id,
            email=request.email,
            name=request.name,
            software_experience=request.software_experience,
            hardware_experience=request.hardware_experience,
            learning_goals=request.learning_goals
        ),
        token=token
    )


@router.post("/auth/signin", response_model=AuthResponse)
async def signin(request: SignInRequest):
    """Sign in to an existing account."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (request.email,))
    row = cursor.fetchone()
    conn.close()

    if not row or not verify_password(request.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create session
    token = create_session(row["id"])

    return AuthResponse(
        user=UserResponse(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            software_experience=row["software_experience"],
            hardware_experience=row["hardware_experience"],
            learning_goals=row["learning_goals"]
        ),
        token=token
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(**user)


@router.put("/auth/profile", response_model=UserResponse)
async def update_profile(request: UpdateProfileRequest, user: dict = Depends(get_current_user)):
    """Update user profile."""
    conn = get_db()
    cursor = conn.cursor()

    updates = []
    values = []

    if request.name is not None:
        updates.append("name = ?")
        values.append(request.name)
    if request.software_experience is not None:
        updates.append("software_experience = ?")
        values.append(request.software_experience)
    if request.hardware_experience is not None:
        updates.append("hardware_experience = ?")
        values.append(request.hardware_experience)
    if request.learning_goals is not None:
        updates.append("learning_goals = ?")
        values.append(request.learning_goals)

    if updates:
        values.append(user["id"])
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()

    # Get updated user
    cursor.execute("SELECT id, email, name, software_experience, hardware_experience, learning_goals FROM users WHERE id = ?", (user["id"],))
    row = cursor.fetchone()
    conn.close()

    return UserResponse(**dict(row))


@router.post("/auth/signout")
async def signout(authorization: str = Header(None)):
    """Sign out and invalidate session."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()

    return {"message": "Signed out successfully"}
