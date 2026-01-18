"""
User Database Module
SQLite database for persistent user storage with chat history JSON file management.
"""

import sqlite3
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

# Database and chat history paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")
DB_PATH = os.path.join(USER_DATA_DIR, "user.db")
CHAT_HISTORY_DIR = os.path.join(USER_DATA_DIR, "chat_history")

# Ensure directories exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)


def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            state TEXT,
            area TEXT,
            category TEXT,
            is_disabled INTEGER DEFAULT 0,
            is_minority INTEGER DEFAULT 0,
            is_student INTEGER DEFAULT 0,
            employment_status TEXT,
            is_govt_employee INTEGER DEFAULT 0,
            annual_income INTEGER,
            family_income INTEGER,
            chat_history_file TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()


# ============ User CRUD Operations ============

def create_user(
    email: str,
    password: str,
    name: str,
    gender: Optional[str] = None,
    age: Optional[int] = None,
    state: Optional[str] = None,
    area: Optional[str] = None,
    category: Optional[str] = None,
    is_disabled: Optional[bool] = None,
    is_minority: Optional[bool] = None,
    is_student: Optional[bool] = None,
    employment_status: Optional[str] = None,
    is_govt_employee: Optional[bool] = None,
    annual_income: Optional[int] = None,
    family_income: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Create a new user in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        user_id = str(uuid.uuid4())
        chat_history_file = f"{user_id}.json"
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO users (
                id, email, password, name, gender, age, state, area, category,
                is_disabled, is_minority, is_student, employment_status,
                is_govt_employee, annual_income, family_income, chat_history_file, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, email.lower().strip(), password, name, gender, age, state, area, category,
            1 if is_disabled else 0,
            1 if is_minority else 0,
            1 if is_student else 0,
            employment_status,
            1 if is_govt_employee else 0,
            annual_income, family_income, chat_history_file, created_at
        ))
        
        conn.commit()
        
        # Create empty chat history file
        chat_file_path = os.path.join(CHAT_HISTORY_DIR, chat_history_file)
        with open(chat_file_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        return {
            "user_id": user_id,
            "email": email.lower().strip(),
            "name": name,
            "chat_history_file": chat_history_file
        }
        
    except sqlite3.IntegrityError:
        return None  # Email already exists
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email address."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def update_user(email: str, **kwargs) -> bool:
    """Update user profile fields."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build dynamic update query
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if value is not None:
            # Convert booleans to integers for SQLite
            if isinstance(value, bool):
                value = 1 if value else 0
            updates.append(f"{key} = ?")
            values.append(value)
    
    if not updates:
        conn.close()
        return True
    
    values.append(email.lower().strip())
    query = f"UPDATE users SET {', '.join(updates)} WHERE email = ?"
    
    cursor.execute(query, values)
    conn.commit()
    affected = cursor.rowcount
    
    if affected == 0:
        # Check if user exists to distinguish between "not found" and "no changes"
        cursor.execute('SELECT 1 FROM users WHERE email = ?', (email.lower().strip(),))
        if cursor.fetchone():
            conn.close()
            return True # User exists, so it was just "no changes"
            
    conn.close()
    
    return affected > 0


# ============ Session Management ============

def create_session(user_id: str, email: str) -> str:
    """Create a new session for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    session_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO sessions (session_id, user_id, email, created_at)
        VALUES (?, ?, ?, ?)
    ''', (session_id, user_id, email.lower().strip(), created_at))
    
    conn.commit()
    conn.close()
    
    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session by session_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def delete_session(session_id: str) -> bool:
    """Delete a session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0


# ============ Chat History Management ============

def get_chat_history(user_id: str) -> List[Dict[str, str]]:
    """Get chat history for a user."""
    user = get_user_by_id(user_id)
    if not user or not user.get('chat_history_file'):
        return []
    
    chat_file_path = os.path.join(CHAT_HISTORY_DIR, user['chat_history_file'])
    
    if not os.path.exists(chat_file_path):
        return []
    
    try:
        with open(chat_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def append_chat_entry(user_id: str, question: str, answer: str) -> bool:
    """Append a Q&A entry to the user's chat history."""
    user = get_user_by_id(user_id)
    if not user or not user.get('chat_history_file'):
        return False
    
    chat_file_path = os.path.join(CHAT_HISTORY_DIR, user['chat_history_file'])
    
    # Load existing history
    history = []
    if os.path.exists(chat_file_path):
        try:
            with open(chat_file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
    
    # Append new entry
    history.append({
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    })
    
    # Keep only last 50 entries to prevent file from growing too large
    if len(history) > 50:
        history = history[-50:]
    
    # Save updated history
    with open(chat_file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return True


def get_user_profile_for_chat(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile data formatted for chatbot context."""
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    return {
        "name": user.get("name"),
        "gender": user.get("gender"),
        "age": user.get("age"),
        "state": user.get("state"),
        "area": user.get("area"),
        "category": user.get("category"),
        "is_disabled": bool(user.get("is_disabled")),
        "is_minority": bool(user.get("is_minority")),
        "is_student": bool(user.get("is_student")),
        "employment_status": user.get("employment_status"),
        "is_govt_employee": bool(user.get("is_govt_employee")),
        "annual_income": user.get("annual_income"),
        "family_income": user.get("family_income")
    }


# Initialize database on module import
init_db()
