"""
Authentication utilities for user registration and login.
"""

import bcrypt
import secrets
from typing import Optional, Tuple
from backend.database import (
    create_user, get_user_by_email, get_user_by_id,
    create_session, get_session, update_session_user, delete_session
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def register_user(name: str, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """
    Register a new user.
    Returns: (success, message, user_id)
    """
    # Check if email already exists
    existing = get_user_by_email(email)
    if existing:
        return False, "Email already registered", None
    
    # Validate inputs
    if not name or len(name) < 2:
        return False, "Name must be at least 2 characters", None
    
    if not email or '@' not in email:
        return False, "Invalid email address", None
    
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters", None
    
    # Create user
    password_hash = hash_password(password)
    user_id = create_user(name, email, password_hash)
    
    return True, "Registration successful", user_id


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Authenticate a user.
    Returns: (success, message, user_data)
    """
    user = get_user_by_email(email)
    
    if not user:
        return False, "Invalid email or password", None
    
    if not verify_password(password, user['password_hash']):
        return False, "Invalid email or password", None
    
    # Return user data without password hash
    user_data = {
        'user_id': user['user_id'],
        'name': user['name'],
        'email': user['email'],
        'created_at': user['created_at']
    }
    
    return True, "Login successful", user_data


def create_user_session(user_id: Optional[str] = None) -> str:
    """Create a new session for a user or anonymous user."""
    return create_session(user_id)


def link_session_to_user(session_id: str, user_id: str) -> bool:
    """Link an anonymous session to a logged-in user."""
    return update_session_user(session_id, user_id)


def validate_session(session_id: str) -> Optional[dict]:
    """
    Validate a session and return user info if logged in.
    Returns: {session_id, user_id, user_name, is_logged_in}
    """
    session = get_session(session_id)
    
    if not session:
        return None
    
    result = {
        'session_id': session['session_id'],
        'user_id': session['user_id'],
        'user_name': None,
        'is_logged_in': False
    }
    
    if session['user_id']:
        user = get_user_by_id(session['user_id'])
        if user:
            result['user_name'] = user['name']
            result['is_logged_in'] = True
    
    return result


def logout(session_id: str) -> bool:
    """Delete a session to log out."""
    return delete_session(session_id)
