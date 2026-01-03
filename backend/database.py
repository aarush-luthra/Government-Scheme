"""
Database setup and models for authentication and session management.
Uses SQLite for simplicity and portability.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "app.db")


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL CHECK (sender IN ('user', 'bot')),
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)
    
    # User profiles table (from Scheme Finder form)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            profile_id TEXT PRIMARY KEY,
            user_id TEXT,
            session_id TEXT NOT NULL,
            name TEXT,
            email TEXT,
            password_hash TEXT,
            gender TEXT,
            age INTEGER,
            state TEXT,
            area TEXT,
            category TEXT,
            is_disabled BOOLEAN DEFAULT 0,
            is_minority BOOLEAN DEFAULT 0,
            is_student BOOLEAN DEFAULT 0,
            employment_status TEXT,
            is_govt_employee BOOLEAN DEFAULT 0,
            annual_income REAL,
            family_income REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)
    
    conn.commit()
    conn.close()


# ============ User Operations ============

def create_user(name: str, email: str, password_hash: str) -> str:
    """Create a new user and return user_id."""
    user_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users (user_id, name, email, password_hash) VALUES (?, ?, ?, ?)",
        (user_id, name, email, password_hash)
    )
    
    conn.commit()
    conn.close()
    return user_id
    

def update_user_profile(session_id: str, profile_data: Dict[str, Any]) -> bool:
    """Update an existing user profile."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Filter out None values or keys you don't want to overwrite (like password if empty)
    fields = []
    values = []
    
    for key, value in profile_data.items():
        # Only update password if a new one is provided (not None)
        if key == 'password_hash' and value is None:
            continue
        
        fields.append(f"{key} = ?")
        values.append(value)
            
    if not fields:
        conn.close()
        return False
        
    values.append(session_id) # For the WHERE clause
    
    try:
        query = f"UPDATE user_profiles SET {', '.join(fields)} WHERE session_id = ?"
        cursor.execute(query, values)
        conn.commit()
        return True
    except Exception as e:
        print(f"Update error: {e}")
        return False
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email address."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, name, email, created_at FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None


# ============ Session Operations ============

def create_session(user_id: Optional[str] = None) -> str:
    """Create a new session (anonymous if user_id is None)."""
    session_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO sessions (session_id, user_id) VALUES (?, ?)",
        (session_id, user_id)
    )
    
    conn.commit()
    conn.close()
    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session by session_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None


def update_session_user(session_id: str, user_id: str) -> bool:
    """Link an anonymous session to a user after login/signup."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE sessions SET user_id = ? WHERE session_id = ?",
        (user_id, session_id)
    )
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def delete_session(session_id: str) -> bool:
    """Delete a session (logout)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ============ Message Operations ============

def save_message(session_id: str, sender: str, content: str) -> str:
    """Save a message and return message_id."""
    message_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO messages (message_id, session_id, sender, content) VALUES (?, ?, ?, ?)",
        (message_id, session_id, sender, content)
    )
    
    conn.commit()
    conn.close()
    return message_id


def get_session_messages(session_id: str) -> List[Dict[str, Any]]:
    """Get all messages for a session, ordered by timestamp."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]


def count_bot_responses(session_id: str) -> int:
    """Count the number of bot responses in a session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) as count FROM messages WHERE session_id = ? AND sender = 'bot'",
        (session_id,)
    )
    row = cursor.fetchone()
    
    conn.close()
    return row['count'] if row else 0


def get_message_summary(session_id: str, limit: int = 5) -> str:
    """Get a summary of recent messages for context injection."""
    messages = get_session_messages(session_id)
    recent = messages[-limit:] if len(messages) > limit else messages
    
    summary_parts = []
    for msg in recent:
        role = "User" if msg['sender'] == 'user' else "Assistant"
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        summary_parts.append(f"{role}: {content}")
    
    return "\n".join(summary_parts)


# ============ Profile Operations ============

def save_user_profile(session_id: str, profile_data: Dict[str, Any], user_id: Optional[str] = None) -> str:
    """Save user profile from Scheme Finder form."""
    profile_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO user_profiles (
            profile_id, user_id, session_id, name, email, password_hash,
            gender, age, state, area, category,
            is_disabled, is_minority, is_student,
            employment_status, is_govt_employee,
            annual_income, family_income
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        profile_id,
        user_id,  # Add user_id
        session_id,
        profile_data.get('name'),
        profile_data.get('email'),
        profile_data.get('password_hash'),
        profile_data.get('gender'),
        profile_data.get('age'),
        profile_data.get('state'),
        profile_data.get('area'),
        profile_data.get('category'),
        profile_data.get('is_disabled', False),
        profile_data.get('is_minority', False),
        profile_data.get('is_student', False),
        profile_data.get('employment_status'),
        profile_data.get('is_govt_employee', False),
        profile_data.get('annual_income'),
        profile_data.get('family_income')
    ))
    
    conn.commit()
    conn.close()
    return profile_id


def get_user_profile(session_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by session_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM user_profiles WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
        (session_id,)
    )
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None


def get_user_profile_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by user_id (persists across sessions)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM user_profiles WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None


# Initialize database on module import
init_db()

