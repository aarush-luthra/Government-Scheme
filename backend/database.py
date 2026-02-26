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
SAVED_SCHEMES_DIR = os.path.join(USER_DATA_DIR, "saved_schemes")
REMINDERS_DIR = os.path.join(USER_DATA_DIR, "reminders")
OFFLINE_FAQ_DIR = os.path.join(USER_DATA_DIR, "offline_faq")

# Ensure directories exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
os.makedirs(SAVED_SCHEMES_DIR, exist_ok=True)
os.makedirs(REMINDERS_DIR, exist_ok=True)
os.makedirs(OFFLINE_FAQ_DIR, exist_ok=True)


def _ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, column_type: str) -> None:
    """Add a table column if it does not already exist."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


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
            role TEXT NOT NULL DEFAULT 'user',
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            alerts_enabled INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_members (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            relationship TEXT,
            gender TEXT,
            age INTEGER,
            category TEXT,
            is_disabled INTEGER DEFAULT 0,
            is_student INTEGER DEFAULT 0,
            employment_status TEXT,
            annual_income INTEGER,
            state TEXT,
            district TEXT,
            pincode TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheme_checklists (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            scheme_name TEXT NOT NULL,
            checklist_json TEXT NOT NULL,
            completion_ratio REAL DEFAULT 0.0,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, scheme_name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_schemes (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            scheme_name TEXT NOT NULL,
            saved_at TEXT NOT NULL,
            last_checked TEXT,
            status TEXT,
            application_status TEXT,
            last_polled_at TEXT,
            deadline TEXT,
            UNIQUE(user_id, scheme_name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheme_locks (
            user_id TEXT PRIMARY KEY,
            scheme_name TEXT,
            is_locked INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            scheme_name TEXT NOT NULL,
            channel TEXT NOT NULL,
            contact TEXT,
            is_active INTEGER DEFAULT 1,
            last_checked TEXT,
            next_deadline TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            endpoint TEXT,
            p256dh TEXT,
            auth TEXT,
            fcm_token TEXT,
            user_agent TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, provider, endpoint, fcm_token),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_events (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            alert_id TEXT,
            scheme_name TEXT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            channel TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_failures (
            id TEXT PRIMARY KEY,
            task_name TEXT NOT NULL,
            payload_json TEXT,
            error_message TEXT NOT NULL,
            retries INTEGER DEFAULT 0,
            is_dead_letter INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feature_usage_events (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            feature_name TEXT NOT NULL,
            success INTEGER DEFAULT 1,
            metadata_json TEXT,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_delivery_attempts (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            alert_id TEXT,
            channel TEXT NOT NULL,
            provider TEXT,
            success INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_ingestion_metrics (
            id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            total_schemes INTEGER DEFAULT 0,
            parser_confidence REAL DEFAULT 0.0,
            broken_links INTEGER DEFAULT 0,
            pending_approvals INTEGER DEFAULT 0,
            published_count INTEGER DEFAULT 0,
            last_run_at TEXT NOT NULL
        )
    ''')

    _ensure_column(conn, "users", "district", "TEXT")
    _ensure_column(conn, "users", "pincode", "TEXT")
    _ensure_column(conn, "users", "role", "TEXT NOT NULL DEFAULT 'user'")
    _ensure_column(conn, "saved_schemes", "application_status", "TEXT")
    _ensure_column(conn, "saved_schemes", "last_polled_at", "TEXT")
    
    conn.commit()
    conn.close()


# ============ User CRUD Operations ============

def create_user(
    email: str,
    password: str,
    name: str,
    role: str = "user",
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
    family_income: Optional[int] = None,
    district: Optional[str] = None,
    pincode: Optional[str] = None
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
                id, email, password, role, name, gender, age, state, area, category,
                is_disabled, is_minority, is_student, employment_status,
                is_govt_employee, annual_income, family_income, district, pincode, chat_history_file, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, email.lower().strip(), password, role, name, gender, age, state, area, category,
            1 if is_disabled else 0,
            1 if is_minority else 0,
            1 if is_student else 0,
            employment_status,
            1 if is_govt_employee else 0,
            annual_income, family_income, district, pincode, chat_history_file, created_at
        ))
        
        conn.commit()
        
        # Create empty chat history file
        chat_file_path = os.path.join(CHAT_HISTORY_DIR, chat_history_file)
        with open(chat_file_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        return {
            "user_id": user_id,
            "email": email.lower().strip(),
            "role": role,
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
        "district": user.get("district"),
        "pincode": user.get("pincode"),
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


def _json_file_for_user(directory: str, user_id: str) -> str:
    return os.path.join(directory, f"{user_id}.json")


def get_saved_schemes(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, scheme_name, saved_at, last_checked, status, application_status, last_polled_at, deadline
        FROM saved_schemes
        WHERE user_id = ?
        ORDER BY saved_at DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_saved_schemes_paginated(user_id: str, limit: int = 20, offset: int = 0):
    """Return (items, total_count) for paginated saved schemes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM saved_schemes WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT id, scheme_name, saved_at, last_checked, status, application_status, last_polled_at, deadline
        FROM saved_schemes
        WHERE user_id = ?
        ORDER BY saved_at DESC
        LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows], total


def save_scheme(user_id: str, scheme_name: str) -> bool:
    if not scheme_name.strip():
        return False
    normalized = scheme_name.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        SELECT id FROM saved_schemes
        WHERE user_id = ? AND lower(scheme_name) = lower(?)
        """,
        (user_id, normalized),
    )
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "UPDATE saved_schemes SET last_checked = ?, status = ? WHERE id = ?",
            (now, "saved", existing["id"]),
        )
        conn.commit()
        conn.close()
        return True
    cursor.execute(
        """
        INSERT INTO saved_schemes (id, user_id, scheme_name, saved_at, last_checked, status, application_status, last_polled_at, deadline)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), user_id, normalized, now, now, "saved", "pending", None, None),
    )
    conn.commit()
    conn.close()
    return True


def update_saved_scheme(
    user_id: str,
    scheme_name: str,
    status: Optional[str] = None,
    deadline: Optional[str] = None,
    last_checked: Optional[str] = None
) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    values: List[Any] = []
    if status is not None:
        updates.append("status = ?")
        values.append(status)
    if deadline is not None:
        updates.append("deadline = ?")
        values.append(deadline)
    updates.append("last_checked = ?")
    values.append(last_checked or datetime.now().isoformat())
    values.extend([user_id, scheme_name.strip()])
    cursor.execute(
        f"UPDATE saved_schemes SET {', '.join(updates)} WHERE user_id = ? AND lower(scheme_name) = lower(?)",
        values,
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def update_saved_scheme_status(user_id: str, scheme_name: str, application_status: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        UPDATE saved_schemes
        SET application_status = ?, last_polled_at = ?, last_checked = ?
        WHERE user_id = ? AND lower(scheme_name) = lower(?)
        """,
        (application_status, now, now, user_id, scheme_name.strip()),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def remove_saved_scheme(user_id: str, scheme_name: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM saved_schemes WHERE user_id = ? AND lower(scheme_name) = lower(?)",
        (user_id, scheme_name.strip()),
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def add_push_subscription(
    user_id: str,
    provider: str,
    endpoint: Optional[str] = None,
    p256dh: Optional[str] = None,
    auth: Optional[str] = None,
    fcm_token: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    now = datetime.now().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    existing_id = None
    cursor.execute(
        """
        SELECT id FROM push_subscriptions
        WHERE user_id = ? AND provider = ? AND ifnull(endpoint, '') = ifnull(?, '') AND ifnull(fcm_token, '') = ifnull(?, '')
        """,
        (user_id, provider, endpoint, fcm_token),
    )
    row = cursor.fetchone()
    if row:
        existing_id = row["id"]
        cursor.execute(
            """
            UPDATE push_subscriptions
            SET p256dh = ?, auth = ?, user_agent = ?, is_active = 1, updated_at = ?
            WHERE id = ?
            """,
            (p256dh, auth, user_agent, now, existing_id),
        )
        subscription_id = existing_id
    else:
        subscription_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO push_subscriptions (
                id, user_id, provider, endpoint, p256dh, auth, fcm_token, user_agent, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (subscription_id, user_id, provider, endpoint, p256dh, auth, fcm_token, user_agent, now, now),
        )
    conn.commit()
    conn.close()
    return {
        "id": subscription_id,
        "user_id": user_id,
        "provider": provider,
        "endpoint": endpoint,
        "fcm_token": fcm_token,
        "updated_at": now,
    }


def get_push_subscriptions(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, provider, endpoint, p256dh, auth, fcm_token, user_agent, is_active, created_at, updated_at
        FROM push_subscriptions
        WHERE user_id = ? AND is_active = 1
        ORDER BY updated_at DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_notification_event(
    user_id: str,
    title: str,
    body: str,
    channel: str,
    scheme_name: Optional[str] = None,
    alert_id: Optional[str] = None,
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    event_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO notification_events (id, user_id, alert_id, scheme_name, title, body, channel, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """,
        (event_id, user_id, alert_id, scheme_name, title, body, channel, now),
    )
    conn.commit()
    conn.close()
    return {
        "id": event_id,
        "user_id": user_id,
        "alert_id": alert_id,
        "scheme_name": scheme_name,
        "title": title,
        "body": body,
        "channel": channel,
        "created_at": now,
    }


def get_notification_events(user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, alert_id, scheme_name, title, body, channel, is_read, created_at
        FROM notification_events
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, max(1, min(limit, 100))),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_saved_schemes() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, scheme_name, saved_at, last_checked, status, application_status, last_polled_at, deadline
        FROM saved_schemes
        ORDER BY saved_at DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def log_task_failure(
    task_name: str,
    payload: Optional[Dict[str, Any]],
    error_message: str,
    retries: int = 0,
    is_dead_letter: bool = False,
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    failure_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO task_failures (id, task_name, payload_json, error_message, retries, is_dead_letter, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            failure_id,
            task_name,
            json.dumps(payload or {}, ensure_ascii=False),
            error_message,
            retries,
            1 if is_dead_letter else 0,
            now,
        ),
    )
    conn.commit()
    conn.close()
    return {
        "id": failure_id,
        "task_name": task_name,
        "retries": retries,
        "is_dead_letter": is_dead_letter,
        "created_at": now,
    }


def get_task_failures(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, task_name, payload_json, error_message, retries, is_dead_letter, created_at
        FROM task_failures
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (max(1, min(limit, 500)),),
    )
    rows = cursor.fetchall()
    conn.close()
    failures = []
    for row in rows:
        item = dict(row)
        try:
            item["payload"] = json.loads(item.pop("payload_json") or "{}")
        except json.JSONDecodeError:
            item["payload"] = {}
        failures.append(item)
    return failures


def track_feature_usage(
    feature_name: str,
    user_id: Optional[str] = None,
    success: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    event_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO feature_usage_events (id, user_id, feature_name, success, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            user_id,
            feature_name,
            1 if success else 0,
            json.dumps(metadata or {}, ensure_ascii=False),
            now,
        ),
    )
    conn.commit()
    conn.close()
    return {"id": event_id, "feature_name": feature_name, "success": success, "created_at": now}


def log_alert_delivery_attempt(
    channel: str,
    success: bool,
    user_id: Optional[str] = None,
    alert_id: Optional[str] = None,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    row_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO alert_delivery_attempts (id, user_id, alert_id, channel, provider, success, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (row_id, user_id, alert_id, channel, provider, 1 if success else 0, now),
    )
    conn.commit()
    conn.close()
    return {"id": row_id, "success": success, "created_at": now}


def get_admin_analytics_summary() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT feature_name, COUNT(*) as count, SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
        FROM feature_usage_events
        GROUP BY feature_name
        ORDER BY count DESC
        """
    )
    feature_rows = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT COUNT(*) as total, SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
        FROM alert_delivery_attempts
        """
    )
    alert_row = dict(cursor.fetchone() or {})
    alert_total = int(alert_row.get("total") or 0)
    alert_success = int(alert_row.get("success_count") or 0)
    alert_success_rate = round((alert_success / alert_total) * 100, 2) if alert_total else 0.0

    cursor.execute("SELECT COUNT(*) as total_saved FROM saved_schemes")
    total_saved_row = cursor.fetchone()
    total_saved = int(dict(total_saved_row).get("total_saved") or 0) if total_saved_row else 0

    cursor.execute(
        """
        SELECT user_id, COUNT(*) as saved_count
        FROM saved_schemes
        GROUP BY user_id
        ORDER BY saved_count DESC
        LIMIT 10
        """
    )
    saved_by_user = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT COUNT(*) as failed_comparisons
        FROM feature_usage_events
        WHERE feature_name = 'scheme_compare' AND success = 0
        """
    )
    failed_row = cursor.fetchone()
    failed_comparisons = int(dict(failed_row).get("failed_comparisons") or 0) if failed_row else 0

    conn.close()

    return {
        "feature_usage": feature_rows,
        "failed_comparisons": failed_comparisons,
        "alert_delivery": {
            "total": alert_total,
            "success": alert_success,
            "success_rate_percent": alert_success_rate,
        },
        "saved_schemes": {
            "total_saved": total_saved,
            "top_users": saved_by_user,
        },
    }


def add_reminder(user_id: str, text: str) -> bool:
    if not text.strip():
        return False
    path = _json_file_for_user(REMINDERS_DIR, user_id)
    reminders = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                reminders = json.load(f)
        except (json.JSONDecodeError, IOError):
            reminders = []
    reminders.append({
        "reminder_text": text.strip(),
        "created_at": datetime.now().isoformat()
    })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)
    return True


def get_reminders(user_id: str) -> List[Dict[str, Any]]:
    path = _json_file_for_user(REMINDERS_DIR, user_id)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def get_alert_preference(user_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT alerts_enabled FROM user_preferences WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    return bool(row["alerts_enabled"])


def set_alert_preference(user_id: str, enabled: bool) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    updated_at = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO user_preferences (user_id, alerts_enabled, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            alerts_enabled = excluded.alerts_enabled,
            updated_at = excluded.updated_at
        """,
        (user_id, 1 if enabled else 0, updated_at)
    )
    conn.commit()
    conn.close()
    return True


def add_alert_subscription(
    user_id: str,
    scheme_name: str,
    channel: str,
    contact: Optional[str] = None,
    next_deadline: Optional[str] = None
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    alert_id = str(uuid.uuid4())
    cursor.execute(
        """
        INSERT INTO alert_subscriptions (
            id, user_id, scheme_name, channel, contact, is_active, last_checked, next_deadline, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
        """,
        (alert_id, user_id, scheme_name.strip(), channel.strip().lower(), contact, now, next_deadline, now, now)
    )
    conn.commit()
    conn.close()
    return {
        "id": alert_id,
        "user_id": user_id,
        "scheme_name": scheme_name.strip(),
        "channel": channel.strip().lower(),
        "contact": contact,
        "next_deadline": next_deadline,
        "last_checked": now
    }


def get_alert_subscriptions(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, scheme_name, channel, contact, is_active, last_checked, next_deadline, created_at, updated_at FROM alert_subscriptions WHERE user_id = ? ORDER BY updated_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_active_alert_subscriptions() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, scheme_name, channel, contact, is_active, last_checked, next_deadline, created_at, updated_at
        FROM alert_subscriptions
        WHERE is_active = 1
        ORDER BY updated_at DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_alert_subscription(alert_id: str, is_active: Optional[bool] = None, next_deadline: Optional[str] = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    values: List[Any] = []
    if is_active is not None:
        updates.append("is_active = ?")
        values.append(1 if is_active else 0)
    if next_deadline is not None:
        updates.append("next_deadline = ?")
        values.append(next_deadline)
    updates.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    values.append(alert_id)
    cursor.execute(f"UPDATE alert_subscriptions SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def touch_alert_last_checked(alert_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "UPDATE alert_subscriptions SET last_checked = ?, updated_at = ? WHERE id = ?",
        (now, now, alert_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def save_checklist(user_id: str, scheme_name: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    checklist_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    total = len(items)
    completed = sum(1 for i in items if i.get("completed"))
    ratio = (completed / total) if total else 0.0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scheme_checklists (id, user_id, scheme_name, checklist_json, completion_ratio, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, scheme_name) DO UPDATE SET
            checklist_json = excluded.checklist_json,
            completion_ratio = excluded.completion_ratio,
            updated_at = excluded.updated_at
        """,
        (checklist_id, user_id, scheme_name.strip(), json.dumps(items, ensure_ascii=False), ratio, now)
    )
    conn.commit()
    conn.close()
    return {
        "user_id": user_id,
        "scheme_name": scheme_name.strip(),
        "items": items,
        "completion_ratio": ratio,
        "updated_at": now
    }


def get_checklist(user_id: str, scheme_name: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT scheme_name, checklist_json, completion_ratio, updated_at FROM scheme_checklists WHERE user_id = ? AND scheme_name = ?",
        (user_id, scheme_name.strip())
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    raw = dict(row)
    return {
        "scheme_name": raw["scheme_name"],
        "items": json.loads(raw["checklist_json"]),
        "completion_ratio": raw["completion_ratio"],
        "updated_at": raw["updated_at"]
    }


def set_scheme_lock(user_id: str, scheme_name: Optional[str], locked: bool) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO scheme_locks (user_id, scheme_name, is_locked, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            scheme_name = excluded.scheme_name,
            is_locked = excluded.is_locked,
            updated_at = excluded.updated_at
        """,
        (user_id, scheme_name, 1 if locked else 0, now)
    )
    conn.commit()
    conn.close()
    return True


def get_scheme_lock(user_id: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT scheme_name, is_locked, updated_at FROM scheme_locks WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"scheme_name": None, "is_locked": False, "updated_at": None}
    raw = dict(row)
    return {
        "scheme_name": raw.get("scheme_name"),
        "is_locked": bool(raw.get("is_locked")),
        "updated_at": raw.get("updated_at"),
    }


def add_family_member(user_id: str, member: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    member_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO family_members (
            id, user_id, name, relationship, gender, age, category, is_disabled,
            is_student, employment_status, annual_income, state, district, pincode, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            member_id, user_id, member.get("name"), member.get("relationship"), member.get("gender"),
            member.get("age"), member.get("category"), 1 if member.get("is_disabled") else 0,
            1 if member.get("is_student") else 0, member.get("employment_status"), member.get("annual_income"),
            member.get("state"), member.get("district"), member.get("pincode"), now, now
        )
    )
    conn.commit()
    conn.close()
    return {"id": member_id, "user_id": user_id, **member, "created_at": now, "updated_at": now}


def get_family_members(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, relationship, gender, age, category, is_disabled, is_student,
               employment_status, annual_income, state, district, pincode, created_at, updated_at
        FROM family_members WHERE user_id = ? ORDER BY created_at ASC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    members = []
    for row in rows:
        item = dict(row)
        item["is_disabled"] = bool(item.get("is_disabled"))
        item["is_student"] = bool(item.get("is_student"))
        members.append(item)
    return members


def delete_family_member(user_id: str, member_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM family_members WHERE user_id = ? AND id = ?", (user_id, member_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def save_offline_faq_pack(user_id: str, payload: Dict[str, Any]) -> bool:
    path = _json_file_for_user(OFFLINE_FAQ_DIR, user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return True


def get_offline_faq_pack(user_id: str) -> Optional[Dict[str, Any]]:
    path = _json_file_for_user(OFFLINE_FAQ_DIR, user_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def upsert_admin_ingestion_metrics(
    source_name: str,
    total_schemes: int,
    parser_confidence: float,
    broken_links: int,
    pending_approvals: int,
    published_count: int
) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    metrics_id = source_name.strip().lower().replace(" ", "_")
    cursor.execute(
        """
        INSERT INTO admin_ingestion_metrics (
            id, source_name, total_schemes, parser_confidence, broken_links, pending_approvals, published_count, last_run_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            total_schemes = excluded.total_schemes,
            parser_confidence = excluded.parser_confidence,
            broken_links = excluded.broken_links,
            pending_approvals = excluded.pending_approvals,
            published_count = excluded.published_count,
            last_run_at = excluded.last_run_at
        """,
        (metrics_id, source_name, total_schemes, parser_confidence, broken_links, pending_approvals, published_count, now)
    )
    conn.commit()
    conn.close()
    return True


def get_admin_ingestion_metrics() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT source_name, total_schemes, parser_confidence, broken_links, pending_approvals, published_count, last_run_at
        FROM admin_ingestion_metrics
        ORDER BY last_run_at DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialize database on module import
init_db()
