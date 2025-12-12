"""
Auth Agent
==========

Manages user authentication and profiles.

Skills:
- getProfile: Get user profile information
- updateProfile: Update user profile
- validateSession: Validate session token
"""

from typing import Any, Dict, List, Optional
import logging
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from .base import BaseAgent, AgentContext, Skill

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "users.db"


class AuthAgent(BaseAgent):
    """
    Agent specialized for authentication and user management.

    This agent handles user authentication, profile management,
    and session validation.
    """

    @property
    def name(self) -> str:
        return "AuthAgent"

    @property
    def description(self) -> str:
        return "Manages user authentication, profiles, and session validation."

    def __init__(self, **kwargs):
        """Initialize auth agent and ensure database exists."""
        super().__init__(**kwargs)
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database."""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    name TEXT,
                    software_experience TEXT DEFAULT 'beginner',
                    hardware_experience TEXT DEFAULT 'beginner',
                    learning_goals TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Auth database initialized")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(32)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return hash_obj.hex(), salt

    def _generate_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)

    def _register_skills(self) -> None:
        """Register authentication skills."""

        # Skill: Get Profile
        async def get_profile_handler(
            context: AgentContext,
            user_id: int = None,
            token: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Get user profile information."""

            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get user by ID or token
                if token:
                    cursor.execute('''
                        SELECT u.* FROM users u
                        JOIN sessions s ON u.id = s.user_id
                        WHERE s.token = ? AND s.expires_at > ?
                    ''', (token, datetime.utcnow()))
                elif user_id:
                    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                else:
                    return {"error": "No user_id or token provided", "success": False}

                user = cursor.fetchone()
                conn.close()

                if user:
                    return {
                        "success": True,
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "name": user["name"],
                            "software_experience": user["software_experience"],
                            "hardware_experience": user["hardware_experience"],
                            "learning_goals": user["learning_goals"],
                            "created_at": user["created_at"],
                        }
                    }

                return {"error": "User not found", "success": False}

            except Exception as e:
                logger.error(f"Get profile error: {e}")
                return {"error": str(e), "success": False}

        self.register_skill(Skill(
            name="getProfile",
            description="Get user profile information by ID or token",
            handler=get_profile_handler,
            output_type="dict",
        ))

        # Skill: Update Profile
        async def update_profile_handler(
            context: AgentContext,
            user_id: int = None,
            token: str = None,
            updates: Dict[str, Any] = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Update user profile."""

            if not updates:
                return {"error": "No updates provided", "success": False}

            allowed_fields = ["name", "software_experience", "hardware_experience", "learning_goals"]
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

            if not filtered_updates:
                return {"error": "No valid fields to update", "success": False}

            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                # Get user_id from token if needed
                if token and not user_id:
                    cursor.execute('''
                        SELECT user_id FROM sessions
                        WHERE token = ? AND expires_at > ?
                    ''', (token, datetime.utcnow()))
                    result = cursor.fetchone()
                    if result:
                        user_id = result[0]
                    else:
                        conn.close()
                        return {"error": "Invalid or expired token", "success": False}

                # Build update query
                set_clause = ", ".join([f"{k} = ?" for k in filtered_updates.keys()])
                values = list(filtered_updates.values()) + [datetime.utcnow(), user_id]

                cursor.execute(f'''
                    UPDATE users SET {set_clause}, updated_at = ?
                    WHERE id = ?
                ''', values)

                conn.commit()
                conn.close()

                return {
                    "success": True,
                    "updated_fields": list(filtered_updates.keys()),
                    "user_id": user_id,
                }

            except Exception as e:
                logger.error(f"Update profile error: {e}")
                return {"error": str(e), "success": False}

        self.register_skill(Skill(
            name="updateProfile",
            description="Update user profile fields",
            handler=update_profile_handler,
            output_type="dict",
        ))

        # Skill: Validate Session
        async def validate_session_handler(
            context: AgentContext,
            token: str,
            **kwargs
        ) -> Dict[str, Any]:
            """Validate a session token."""

            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT s.*, u.email, u.name, u.software_experience,
                           u.hardware_experience, u.learning_goals
                    FROM sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.token = ?
                ''', (token,))

                session = cursor.fetchone()
                conn.close()

                if not session:
                    return {"valid": False, "error": "Session not found"}

                # Check expiration
                expires_at = datetime.fromisoformat(session["expires_at"])
                if expires_at < datetime.utcnow():
                    return {"valid": False, "error": "Session expired"}

                return {
                    "valid": True,
                    "user_id": session["user_id"],
                    "email": session["email"],
                    "name": session["name"],
                    "software_experience": session["software_experience"],
                    "hardware_experience": session["hardware_experience"],
                    "learning_goals": session["learning_goals"],
                    "expires_at": session["expires_at"],
                }

            except Exception as e:
                logger.error(f"Session validation error: {e}")
                return {"valid": False, "error": str(e)}

        self.register_skill(Skill(
            name="validateSession",
            description="Validate a session token and return user info",
            handler=validate_session_handler,
            output_type="dict",
        ))

        # Skill: Create Session
        async def create_session_handler(
            context: AgentContext,
            email: str,
            password: str,
            **kwargs
        ) -> Dict[str, Any]:
            """Create a new session (sign in)."""

            try:
                conn = sqlite3.connect(str(DB_PATH))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get user
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
                user = cursor.fetchone()

                if not user:
                    conn.close()
                    return {"success": False, "error": "User not found"}

                # Verify password
                password_hash, _ = self._hash_password(password, user["salt"])
                if password_hash != user["password_hash"]:
                    conn.close()
                    return {"success": False, "error": "Invalid password"}

                # Create session
                token = self._generate_token()
                expires_at = datetime.utcnow() + timedelta(days=7)

                cursor.execute('''
                    INSERT INTO sessions (user_id, token, expires_at)
                    VALUES (?, ?, ?)
                ''', (user["id"], token, expires_at))

                conn.commit()
                conn.close()

                return {
                    "success": True,
                    "token": token,
                    "expires_at": expires_at.isoformat(),
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "name": user["name"],
                        "software_experience": user["software_experience"],
                        "hardware_experience": user["hardware_experience"],
                        "learning_goals": user["learning_goals"],
                    }
                }

            except Exception as e:
                logger.error(f"Create session error: {e}")
                return {"success": False, "error": str(e)}

        self.register_skill(Skill(
            name="createSession",
            description="Sign in and create a new session",
            handler=create_session_handler,
            output_type="dict",
        ))

        # Skill: Register User
        async def register_user_handler(
            context: AgentContext,
            email: str,
            password: str,
            name: str = None,
            software_experience: str = "beginner",
            hardware_experience: str = "beginner",
            learning_goals: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Register a new user."""

            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                # Check if user exists
                cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
                if cursor.fetchone():
                    conn.close()
                    return {"success": False, "error": "Email already registered"}

                # Hash password
                password_hash, salt = self._hash_password(password)

                # Insert user
                cursor.execute('''
                    INSERT INTO users (email, password_hash, salt, name,
                                      software_experience, hardware_experience, learning_goals)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (email, password_hash, salt, name, software_experience,
                      hardware_experience, learning_goals))

                user_id = cursor.lastrowid

                # Create session
                token = self._generate_token()
                expires_at = datetime.utcnow() + timedelta(days=7)

                cursor.execute('''
                    INSERT INTO sessions (user_id, token, expires_at)
                    VALUES (?, ?, ?)
                ''', (user_id, token, expires_at))

                conn.commit()
                conn.close()

                return {
                    "success": True,
                    "token": token,
                    "expires_at": expires_at.isoformat(),
                    "user": {
                        "id": user_id,
                        "email": email,
                        "name": name,
                        "software_experience": software_experience,
                        "hardware_experience": hardware_experience,
                        "learning_goals": learning_goals,
                    }
                }

            except Exception as e:
                logger.error(f"Register user error: {e}")
                return {"success": False, "error": str(e)}

        self.register_skill(Skill(
            name="registerUser",
            description="Register a new user account",
            handler=register_user_handler,
            output_type="dict",
        ))

        # Skill: Delete Session (Sign Out)
        async def delete_session_handler(
            context: AgentContext,
            token: str,
            **kwargs
        ) -> Dict[str, Any]:
            """Delete a session (sign out)."""

            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
                deleted = cursor.rowcount

                conn.commit()
                conn.close()

                return {
                    "success": deleted > 0,
                    "message": "Signed out successfully" if deleted > 0 else "Session not found",
                }

            except Exception as e:
                logger.error(f"Delete session error: {e}")
                return {"success": False, "error": str(e)}

        self.register_skill(Skill(
            name="deleteSession",
            description="Sign out by deleting the session",
            handler=delete_session_handler,
            output_type="dict",
        ))
