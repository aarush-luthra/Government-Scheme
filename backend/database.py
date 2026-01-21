"""
User Database Module (PostgreSQL)
Stateless database implementation for Render deployment.
"""

import os
import uuid
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set!")
        raise ValueError("DATABASE_URL not set")
    
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def init_db():
    """Initialize the database with required tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # User Table
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
                is_disabled BOOLEAN DEFAULT FALSE,
                is_minority BOOLEAN DEFAULT FALSE,
                is_student BOOLEAN DEFAULT FALSE,
                employment_status TEXT,
                is_govt_employee BOOLEAN DEFAULT FALSE,
                annual_income INTEGER,
                family_income INTEGER,
                created_at TIMESTAMP NOT NULL
            )
        ''')
        
        # Sessions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                email TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
        ''')
        
        # Chat History Table (New)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

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
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        cursor.execute('''
            INSERT INTO users (
                id, email, password, name, gender, age, state, area, category,
                is_disabled, is_minority, is_student, employment_status,
                is_govt_employee, annual_income, family_income, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            user_id, email.lower().strip(), password, name, gender, age, state, area, category,
            is_disabled, is_minority, is_student, employment_status,
            is_govt_employee, annual_income, family_income, created_at
        ))
        
        conn.commit()
        
        return {
            "user_id": user_id,
            "email": email.lower().strip(),
            "name": name
        }
        
    except psycopg2.IntegrityError:
        if conn:
            conn.rollback()
        return None  # Email already exists
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email address."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = %s', (email.lower().strip(),))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None
    finally:
        if conn:
            conn.close()


def update_user(email: str, **kwargs) -> bool:
    """Update user profile fields."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if value is not None:
                updates.append(f"{key} = %s")
                values.append(value)
        
        if not updates:
            return True
        
        values.append(email.lower().strip())
        query = f"UPDATE users SET {', '.join(updates)} WHERE email = %s"
        
        cursor.execute(query, values)
        conn.commit()
        affected = cursor.rowcount
        
        if affected == 0:
            # Check if user exists
            cursor.execute('SELECT 1 FROM users WHERE email = %s', (email.lower().strip(),))
            if cursor.fetchone():
                return True # User exists, no changes needed
                
        return affected > 0
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


# ============ Session Management ============

def create_session(user_id: str, email: str) -> str:
    """Create a new session for a user."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        session_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, email, created_at)
            VALUES (%s, %s, %s, %s)
        ''', (session_id, user_id, email.lower().strip(), created_at))
        
        conn.commit()
        return session_id
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session by session_id."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE session_id = %s', (session_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        return None
    finally:
        if conn:
            conn.close()


def delete_session(session_id: str) -> bool:
    """Delete a session."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_id = %s', (session_id,))
        conn.commit()
        affected = cursor.rowcount
        return affected > 0
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


# ============ Chat History Management ============

def get_chat_history(user_id: str) -> List[Dict[str, str]]:
    """Get chat history for a user."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get last 50 messages ordered by time
        cursor.execute('''
            SELECT question, answer, timestamp 
            FROM chat_history 
            WHERE user_id = %s 
            ORDER BY timestamp ASC 
            LIMIT 50
        ''', (user_id,))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                "question": row["question"],
                "answer": row["answer"],
                "timestamp": row["timestamp"].isoformat() if isinstance(row["timestamp"], datetime) else row["timestamp"]
            })
            
        return history
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return []
    finally:
        if conn:
            conn.close()


def append_chat_entry(user_id: str, question: str, answer: str) -> bool:
    """Append a Q&A entry to the user's chat history."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now()
        
        cursor.execute('''
            INSERT INTO chat_history (user_id, question, answer, timestamp)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, question, answer, timestamp))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error appending chat entry: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


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


# Attempt initialization if URL is set (safe import)
if os.getenv("DATABASE_URL"):
    init_db()
else:
    logger.warning("DATABASE_URL not set. Database not initialized.")
