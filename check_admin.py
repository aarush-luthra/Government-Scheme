from backend import database as db
import uuid
from backend.database import get_db

admin_email = f"admin_{uuid.uuid4().hex[:10]}@example.com"
admin_user = db.create_user(
    email=admin_email,
    password="password123",
    name="Admin User",
    role="admin",
)
print(f"Created Admin Email: {admin_email}")
print("Password: password123")
