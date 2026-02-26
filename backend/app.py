from fastapi import FastAPI, HTTPException, Request, Response, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import uuid
import json
# Fix for OpenMP runtime conflict on macOS
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from backend.nlp.indicbart import IndicBartTranslator
from backend.rag.retriever import VectorStoreRetriever
from backend.rag.generator import generate_answer
from backend.rag.scheme_matcher import SchemeMatcher
from backend import database as db  # Import database module
from backend.notifications import dispatch_alert
from backend.routes.ocr_routes import router as ocr_router  # Import OCR routes
from dotenv import load_dotenv
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
import re
from datetime import datetime
from langchain_core.documents import Document
import threading
import time
import hashlib
from contextlib import asynccontextmanager
from backend.auth import create_access_token, create_refresh_token, decode_token, decode_refresh_token, require_role, Role, resolve_user_from_request
import difflib
from backend.worker.queue import get_queue
from backend.worker.tasks import process_deadline_alerts, poll_scheme_statuses
from rq.job import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


@asynccontextmanager
async def _app_lifespan(_: FastAPI):
    if os.getenv("APP_TEST_MODE", "0") != "1":
        enabled = os.getenv("AUTO_ALERT_DISPATCH_ENABLED", "0").strip() == "1"
        if enabled:
            interval_minutes = int(os.getenv("AUTO_ALERT_DISPATCH_INTERVAL_MIN", "60"))
            interval_seconds = max(60, interval_minutes * 60)
            thread = threading.Thread(target=_auto_dispatch_loop, args=(interval_seconds,), daemon=True)
            thread.start()
            logger.info("Auto alert dispatcher thread initialized")
    yield


# ---- Rate Limiter Setup ---- #
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="Government Scheme Assistant",
    description="Multi-language AI assistant for Indian government schemes",
    version="2.0.0",
    lifespan=_app_lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_API_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL_SECONDS = int(os.getenv("API_CACHE_TTL_SECONDS", "30"))


def _cache_key(prefix: str, payload: Dict[str, Any]) -> str:
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha1(blob.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def _cache_get(key: str) -> Optional[Any]:
    item = _API_CACHE.get(key)
    if not item:
        return None
    if time.time() >= item["expires_at"]:
        _API_CACHE.pop(key, None)
        return None
    return item["value"]


def _cache_set(key: str, value: Any, ttl: int = _CACHE_TTL_SECONDS) -> None:
    _API_CACHE[key] = {"value": value, "expires_at": time.time() + max(1, ttl)}


@app.middleware("http")
async def enforce_admin_permissions(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/v1/admin/"):
        user = resolve_user_from_request(
            request=request,
            authorization=request.headers.get("Authorization"),
        )
        if not user:
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        if str(user.get("role") or Role.USER) != Role.ADMIN:
            return JSONResponse(status_code=403, content={"detail": "Insufficient permissions"})
    return await call_next(request)


@app.middleware("http")
async def request_telemetry(request: Request, call_next):
    request_id = str(uuid.uuid4())
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.error(
            json.dumps(
                {
                    "event": "request_error",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                }
            )
        )
        db.log_task_failure(
            task_name="http_request",
            payload={"method": request.method, "path": request.url.path, "request_id": request_id},
            error_message=str(exc),
            retries=0,
            is_dead_letter=False,
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "event": "request_completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        )
    )
    response.headers["X-Request-ID"] = request_id
    return response

# Initialize translator (single instance for efficiency)
if os.getenv("APP_TEST_MODE", "0") == "1":
    class _DummyTranslator:
        SUPPORTED_LANGUAGES = {"en_XX": "English"}
        device = "cpu"
        model_name = "dummy-translator"

        @staticmethod
        def get_supported_languages():
            return {"en_XX": "English"}

        @staticmethod
        def detect_language_code(text: str):
            return "en_XX"

        @staticmethod
        def to_english(text: str, source_lang: str = "en_XX"):
            return text

        @staticmethod
        def from_english(text: str, target_lang: str = "en_XX"):
            return text

        @staticmethod
        def translate(text: str, source_lang: str = "en_XX", target_lang: str = "en_XX"):
            return text

        @staticmethod
        def batch_translate(texts: List[str], source_lang: str = "en_XX", target_lang: str = "en_XX"):
            return texts

    class _DummyRetriever:
        @staticmethod
        def _doc(title: str):
            return Document(
                page_content="Eligibility: Any citizen. Documents: ID proof. Deadline: Not specified. Apply via official portal.",
                metadata={
                    "scheme_name": title,
                    "title": title,
                    "eligibility": "Any citizen",
                    "benefits": "Demo benefit",
                    "documents_required": "ID Proof, Address Proof",
                    "deadline": "Not specified",
                    "official_site": "https://example.org",
                    "apply_link": "https://example.org/apply",
                    "category": "General",
                    "source": "test-source",
                    "match_confidence": 0.8
                }
            )

        def search(self, query: str, k: int = 4):
            return [self._doc("PM Kisan"), self._doc("Atal Pension Yojana"), self._doc("Mudra Loan")][:k]

        def search_by_profile(self, user_profile: Dict, query: Optional[str] = None, k: int = 20):
            return self.search(query or "profile", k=k)

    translator = _DummyTranslator()
else:
    translator = IndicBartTranslator()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize retriever
retriever = _DummyRetriever() if os.getenv("APP_TEST_MODE", "0") == "1" else VectorStoreRetriever()

# Determine frontend path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount frontend static files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Include OCR router
app.include_router(ocr_router, prefix="/api/v1", tags=["OCR"])

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204) # No content, stops 404 logs

# ============ Request/Response Models ============
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's question or message")
    source_lang: Optional[str] = Field(None, description="Source language code (auto-detect if null)")
    target_lang: Optional[str] = Field(None, description="Preferred response language. If null, defaults to source language.")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Chat history (list of role/content dicts)")
    user_profile: Optional[Dict[str, Any]] = Field(default=None, description="User profile data for personalization")
    user_id: Optional[str] = Field(default=None, description="User ID for loading profile and persisting chat history")
    scheme_lock: Optional[str] = Field(default=None, description="Locked scheme for multi-turn focus")


class ChatResponse(BaseModel):
    reply: str
    detected_language: Optional[str] = None
    language_name: Optional[str] = None
    original_message: Optional[str] = None
    translated_message: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    source_lang: Optional[str] = None
    target_lang: str = Field("en_XX", description="Target language code")


class TranslateResponse(BaseModel):
    translation: str
    source_lang: str
    target_lang: str


class BatchTranslateRequest(BaseModel):
    texts: List[str]
    source_lang: Optional[str] = None
    target_lang: str = "en_XX"


class LanguageInfo(BaseModel):
    code: str
    name: str


# ============ Auth Request/Response Models ============
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AdminDispatchRequest(BaseModel):
    token: Optional[str] = None


class ProfileRequest(BaseModel):
    """Request model for creating/updating user profile"""
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)
    gender: Optional[str] = None
    age: Optional[int] = None
    state: Optional[str] = None
    area: Optional[str] = None
    category: Optional[str] = None
    is_disabled: Optional[bool] = None
    is_minority: Optional[bool] = None
    is_student: Optional[bool] = None
    employment_status: Optional[str] = None
    is_govt_employee: Optional[bool] = None
    annual_income: Optional[int] = None
    family_income: Optional[int] = None
    district: Optional[str] = None
    pincode: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    """Request model for updating profile (password optional)"""
    name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    state: Optional[str] = None
    area: Optional[str] = None
    category: Optional[str] = None
    is_disabled: Optional[bool] = None
    is_minority: Optional[bool] = None
    is_student: Optional[bool] = None
    employment_status: Optional[str] = None
    is_govt_employee: Optional[bool] = None
    annual_income: Optional[int] = None
    family_income: Optional[int] = None
    district: Optional[str] = None
    pincode: Optional[str] = None


class SchemeCompareRequest(BaseModel):
    scheme_names: List[str] = Field(..., min_length=2, max_length=3)
    state: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None


class SchemeSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    limit: int = Field(default=8, ge=1, le=20)


class ChecklistRequest(BaseModel):
    scheme_name: str
    items: Optional[List[Dict[str, Any]]] = None


class ReminderRequest(BaseModel):
    reminder_text: str


class AlertSubscriptionRequest(BaseModel):
    scheme_name: str
    channel: str = Field(default="in_app", description="in_app | email | push")
    contact: Optional[str] = None
    next_deadline: Optional[str] = None


class PushSubscriptionRequest(BaseModel):
    provider: str = Field(default="fcm", description="fcm | webpush")
    endpoint: Optional[str] = None
    p256dh: Optional[str] = None
    auth: Optional[str] = None
    fcm_token: Optional[str] = None
    user_agent: Optional[str] = None


class FamilyMemberRequest(BaseModel):
    name: str
    relationship: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    category: Optional[str] = None
    is_disabled: Optional[bool] = None
    is_student: Optional[bool] = None
    employment_status: Optional[str] = None
    annual_income: Optional[int] = None
    state: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None


class TestBootstrapUserRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = Role.USER


class PrefillRequest(BaseModel):
    scheme_name: str
    profile_data: Optional[Dict[str, Any]] = None
    ocr_fields: Optional[Dict[str, Any]] = None


class EligibilitySimulationRequest(BaseModel):
    overrides: Dict[str, Any]
    top_k: int = 5


class RejectionExplainRequest(BaseModel):
    scheme_name: str


class SchemeLockRequest(BaseModel):
    scheme_name: Optional[str] = None
    is_locked: bool = False


# ============ Auth Helper Functions ============
def get_session_from_cookie(request: Request) -> Optional[dict]:
    """Extract session data from cookie"""
    session_id = request.cookies.get("session_id")
    if session_id:
        return db.get_session(session_id)
    return None


# ============ Auth Endpoints ============
@app.get("/auth/me")
async def auth_check(request: Request):
    """Check current authentication status"""
    anonymous_session_id = str(uuid.uuid4())

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):].strip()
        try:
            payload = decode_token(token)
            user = db.get_user_by_id(str(payload.get("sub")))
            if user:
                return {
                    "is_logged_in": True,
                    "user_id": user["id"],
                    "user_name": user["name"],
                    "role": user.get("role", Role.USER),
                    "session_id": request.cookies.get("session_id") or anonymous_session_id
                }
        except HTTPException:
            pass

    session = get_session_from_cookie(request)
    if session:
        user = db.get_user_by_email(session["email"])
        if user:
            return {
                "is_logged_in": True,
                "user_id": user["id"],
                "user_name": user["name"],
                "role": user.get("role", Role.USER),
                "session_id": request.cookies.get("session_id")
            }

    return {
        "is_logged_in": False,
        "session_id": anonymous_session_id
    }


@app.post("/auth/login")
@limiter.limit("5/minute")
async def auth_login(request: Request, req: LoginRequest, response: Response):
    """Sign in with email and password"""
    email = req.email.lower().strip()
    
    # Check if user exists
    user = db.get_user_by_email(email)
    if not user:
        return {"success": False, "message": "No account found with this email. Please sign up first."}
    
    # Check password (simple comparison - production should use bcrypt)
    if user["password"] != req.password:
        return {"success": False, "message": "Incorrect password. Please try again."}
    
    # Create session
    session_id = db.create_session(user["id"], email)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 days
    )
    
    access_token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user.get("role", Role.USER),
    )

    refresh_token = create_refresh_token(
        user_id=user["id"],
        email=user["email"],
        role=user.get("role", Role.USER),
    )

    logger.info(f"User logged in: {email}")
    
    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "user_id": user["id"],
            "name": user["name"],
            "role": user.get("role", Role.USER),
        }
    }


class RefreshRequest(BaseModel):
    refresh_token: str


@app.post("/auth/refresh")
async def auth_refresh(req: RefreshRequest):
    """Exchange a valid refresh token for a new access token."""
    payload = decode_refresh_token(req.refresh_token)
    user = db.get_user_by_id(str(payload.get("sub")))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    new_access = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user.get("role", Role.USER),
    )
    return {"success": True, "access_token": new_access}


@app.post("/auth/logout")
async def auth_logout(request: Request, response: Response):
    """Log out and clear session"""
    session_id = request.cookies.get("session_id")
    
    # Remove session from storage
    if session_id:
        db.delete_session(session_id)
    
    # Clear the cookie
    response.delete_cookie(key="session_id")
    
    logger.info("User logged out")
    return {"success": True}


@app.post("/profile")
@limiter.limit("5/minute")
async def create_profile(request: Request, req: ProfileRequest, response: Response):
    """Create a new user profile (sign up)"""
    email = req.email.lower().strip()
    
    # Create user in database
    result = db.create_user(
        email=email,
        password=req.password,
        name=req.name,
        role=Role.USER,
        gender=req.gender,
        age=req.age,
        state=req.state,
        area=req.area,
        category=req.category,
        is_disabled=req.is_disabled,
        is_minority=req.is_minority,
        is_student=req.is_student,
        employment_status=req.employment_status,
        is_govt_employee=req.is_govt_employee,
        annual_income=req.annual_income,
        family_income=req.family_income,
        district=req.district,
        pincode=req.pincode
    )
    
    if not result:
        return {"success": False, "message": "An account with this email already exists. Please sign in."}
    
    user_id = result["user_id"]
    access_token = create_access_token(user_id=user_id, email=email, role=Role.USER)
    
    # Auto-login: create session
    session_id = db.create_session(user_id, email)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 days
    )
    
    logger.info(f"New user created: {email}")
    
    return {
        "success": True,
        "user_id": user_id,
        "access_token": access_token,
        "role": Role.USER
    }


@app.post("/test/bootstrap-user")
async def test_bootstrap_user(req: TestBootstrapUserRequest):
    if os.getenv("APP_TEST_MODE", "0") != "1":
        raise HTTPException(status_code=404, detail="Not found")
    user = db.get_user_by_email(req.email)
    if not user:
        created = db.create_user(
            email=req.email,
            password=req.password,
            name=req.name,
            role=req.role,
        )
        if not created:
            raise HTTPException(status_code=400, detail="Could not create test user")
        user = db.get_user_by_email(req.email)
    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user.get("role", Role.USER),
    )
    return {"success": True, "token": token, "role": user.get("role", Role.USER), "user_id": user["id"]}


@app.get("/edit")
async def get_profile(request: Request):
    """Get current user's profile for editing"""
    session = get_session_from_cookie(request)
    
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.get_user_by_email(session["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return profile data (exclude password)
    return {
        "user_id": user.get("user_id") or user.get("email"),
        "email": user.get("email"),
        "name": user.get("name"),
        "gender": user.get("gender"),
        "age": user.get("age"),
        "state": user.get("state"),
        "area": user.get("area"),
        "category": user.get("category"),
        "is_disabled": user.get("is_disabled"),
        "is_minority": user.get("is_minority"),
        "is_student": user.get("is_student"),
        "employment_status": user.get("employment_status"),
        "is_govt_employee": user.get("is_govt_employee"),
        "annual_income": user.get("annual_income"),
        "family_income": user.get("family_income"),
        "district": user.get("district"),
        "pincode": user.get("pincode")
    }


@app.post("/edit")
async def update_profile(req: ProfileUpdateRequest, request: Request):
    """Update current user's profile"""
    session = get_session_from_cookie(request)
    
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.get_user_by_email(session["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    update_data = req.model_dump(exclude_unset=True)
    if "email" in update_data:
        del update_data["email"]  # Prevent duplicate argument error
    success = db.update_user(session["email"], **update_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    
    logger.info(f"Profile updated: {session['email']}")
    
    return {"success": True, "message": "Profile updated successfully"}


# API Endpoints

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/auth/login")
async def serve_login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/signup")
async def serve_signup_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))

@app.get("/profile")
async def serve_profile_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))

@app.get("/onboarding")
async def serve_onboarding():
    return FileResponse(os.path.join(FRONTEND_DIR, "onboarding.html"))

@app.get("/saved")
async def serve_saved_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "saved.html"))

@app.get("/admin")
async def serve_admin_console():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))


# ---- Serve root-level frontend assets (CSS / JS) ----
@app.get("/style.css")
async def serve_style_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "style.css"), media_type="text/css")


@app.get("/script.js")
async def serve_script_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "script.js"), media_type="application/javascript")


@app.get("/translations.js")
async def serve_translations_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "translations.js"), media_type="application/javascript")


@app.get("/{filename}.html")
async def serve_html_page(filename: str):
    filepath = os.path.join(FRONTEND_DIR, f"{filename}.html")
    if os.path.isfile(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/health")
async def health_check():
    checks = {}
    overall = "healthy"

    # 1. SQLite writable check
    try:
        import sqlite3
        db_path = os.path.join(BASE_DIR, "backend", "user_data", "user.db")
        conn = sqlite3.connect(db_path, timeout=2)
        conn.execute("SELECT 1")
        conn.close()
        checks["sqlite"] = {"status": "ok"}
    except Exception as e:
        checks["sqlite"] = {"status": "error", "detail": str(e)}
        overall = "degraded"

    # 2. FAISS index check
    try:
        if retriever and hasattr(retriever, 'search'):
            test_docs = retriever.search("test", k=1)
            checks["faiss"] = {"status": "ok", "documents_accessible": len(test_docs) > 0}
        else:
            checks["faiss"] = {"status": "not_loaded"}
            overall = "degraded"
    except Exception as e:
        checks["faiss"] = {"status": "error", "detail": str(e)}
        overall = "degraded"

    # 3. Translation model check
    try:
        supported = translator.get_supported_languages()
        checks["translator"] = {"status": "ok", "languages": len(supported)}
    except Exception as e:
        checks["translator"] = {"status": "error", "detail": str(e)}
        overall = "degraded"

    status_code = 200 if overall == "healthy" else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "service": "Government Scheme Assistant",
            "components": checks
        }
    )

@app.get("/languages", response_model=List[LanguageInfo])
async def get_supported_languages():
    languages = translator.get_supported_languages()
    return [
        LanguageInfo(code=code, name=name) 
        for code, name in languages.items()
    ]


@app.post("/translate", response_model=TranslateResponse)
@limiter.limit("20/minute")
async def translate_text(request: Request, req: TranslateRequest):
    try:
        if req.source_lang is None:
            detected_lang = translator.detect_language_code(req.text)
            if detected_lang is None:
                raise HTTPException(status_code=400, detail="Could not detect source language.")
            source_lang = detected_lang
        else:
            source_lang = req.source_lang
        
        supported = translator.get_supported_languages()
        if source_lang not in supported:
            raise HTTPException(status_code=400, detail=f"Unsupported source language: {source_lang}")
        if req.target_lang not in supported:
            raise HTTPException(status_code=400, detail=f"Unsupported target language: {req.target_lang}")
        
        cache_key = _cache_key("translate", {"text": req.text, "src": source_lang, "tgt": req.target_lang})
        cached = _cache_get(cache_key)
        if cached is not None:
            return TranslateResponse(**cached)

        translation = translator.translate(req.text, source_lang=source_lang, target_lang=req.target_lang)
        result = {"translation": translation, "source_lang": source_lang, "target_lang": req.target_lang}
        _cache_set(cache_key, result, ttl=120)
        
        return TranslateResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail="Translation failed")


@app.post("/translate/batch")
async def batch_translate(req: BatchTranslateRequest):
    try:
        cache_key = _cache_key("batch_translate", {"texts": req.texts, "src": req.source_lang, "tgt": req.target_lang})
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached

        translations = translator.batch_translate(req.texts, source_lang=req.source_lang, target_lang=req.target_lang)
        result = {
            "translations": translations,
            "count": len(translations),
            "source_lang": req.source_lang,
            "target_lang": req.target_lang
        }
        _cache_set(cache_key, result, ttl=120)
        return result
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail="Batch translation failed")


def _require_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):].strip()
        payload = decode_token(token)
        user = db.get_user_by_id(str(payload.get("sub")))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return str(user["id"])

    session = get_session_from_cookie(request)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.get_user_by_email(session["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return str(user["id"])


def _dispatch_alerts_for_items(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deliveries = []
    for alert in alerts:
        if not alert.get("is_active"):
            continue
        result = dispatch_alert(alert)
        db.touch_alert_last_checked(alert["id"])
        deliveries.append({
            "alert_id": alert["id"],
            "user_id": alert.get("user_id"),
            "scheme_name": alert.get("scheme_name"),
            "channel": alert.get("channel"),
            "result": result
        })
    return deliveries


def _enqueue_or_run(task_name: str, kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    task_kwargs = kwargs or {}
    if os.getenv("APP_TEST_MODE", "0") == "1" or os.getenv("WORKER_SYNC_FALLBACK", "0") == "1":
        if task_name == "process_deadline_alerts":
            return {"mode": "sync", "result": process_deadline_alerts(**task_kwargs)}
        if task_name == "poll_scheme_statuses":
            return {"mode": "sync", "result": poll_scheme_statuses(**task_kwargs)}
        raise ValueError(f"Unknown task: {task_name}")
    try:
        queue = get_queue()
        fn = process_deadline_alerts if task_name == "process_deadline_alerts" else poll_scheme_statuses
        job = queue.enqueue(fn, kwargs=task_kwargs, retry=Retry(max=2, interval=[5, 15]))
        return {"mode": "queued", "job_id": job.id}
    except Exception as exc:
        db.log_task_failure(task_name=task_name, payload=task_kwargs, error_message=str(exc), retries=0, is_dead_letter=False)
        logger.warning("Queue unavailable. Falling back to sync for task=%s err=%s", task_name, exc)
        if task_name == "process_deadline_alerts":
            return {"mode": "sync_fallback", "result": process_deadline_alerts(**task_kwargs)}
        return {"mode": "sync_fallback", "result": poll_scheme_statuses(**task_kwargs)}


def _auto_dispatch_loop(interval_seconds: int) -> None:
    logger.info(f"Auto alert dispatcher started (interval={interval_seconds}s)")
    while True:
        try:
            active = db.get_all_active_alert_subscriptions()
            _dispatch_alerts_for_items(active)
        except Exception as exc:
            logger.error(f"Auto alert dispatch failed: {exc}")
        time.sleep(interval_seconds)


@app.get("/api/v1/saved-dashboard")
async def saved_dashboard(request: Request, limit: int = 20, offset: int = 0):
    user_id = _require_user_id(request)
    schemes, total_schemes = db.get_saved_schemes_paginated(user_id, limit, offset)
    return {
        "saved_schemes": schemes,
        "total_schemes": total_schemes,
        "reminders": db.get_reminders(user_id),
        "alerts": db.get_alert_subscriptions(user_id),
        "notifications": db.get_notification_events(user_id, limit=limit),
        "scheme_lock": db.get_scheme_lock(user_id),
        "pagination": {"limit": limit, "offset": offset, "total": total_schemes},
        "last_synced_at": datetime.now().isoformat()
    }


@app.post("/api/v1/saved-schemes")
async def save_scheme_from_api(payload: Dict[str, Any], request: Request):
    user_id = _require_user_id(request)
    scheme_name = str(payload.get("scheme_name") or "").strip()
    if not scheme_name:
        raise HTTPException(status_code=400, detail="scheme_name is required")
    db.save_scheme(user_id, scheme_name)
    db.track_feature_usage("save_scheme", user_id=user_id, success=True, metadata={"scheme_name": scheme_name})
    return {"success": True, "saved_schemes": db.get_saved_schemes(user_id)}


@app.delete("/api/v1/saved-schemes/{scheme_name}")
async def delete_saved_scheme(scheme_name: str, request: Request):
    user_id = _require_user_id(request)
    ok = db.remove_saved_scheme(user_id, scheme_name)
    db.track_feature_usage("unsave_scheme", user_id=user_id, success=ok, metadata={"scheme_name": scheme_name})
    return {"success": ok, "saved_schemes": db.get_saved_schemes(user_id)}


@app.post("/api/v1/reminders")
async def add_reminder_api(req: ReminderRequest, request: Request):
    user_id = _require_user_id(request)
    db.add_reminder(user_id, req.reminder_text)
    return {"success": True, "reminders": db.get_reminders(user_id)}


@app.post("/api/v1/alerts/subscriptions")
async def create_alert_subscription(req: AlertSubscriptionRequest, request: Request):
    user_id = _require_user_id(request)
    alert = db.add_alert_subscription(
        user_id=user_id,
        scheme_name=req.scheme_name,
        channel=req.channel,
        contact=req.contact,
        next_deadline=req.next_deadline
    )
    db.set_alert_preference(user_id, True)
    initial_delivery = dispatch_alert(alert)
    db.touch_alert_last_checked(alert["id"])
    return {"success": True, "alert": alert, "initial_delivery": initial_delivery, "alerts": db.get_alert_subscriptions(user_id)}


@app.post("/api/v1/push/subscribe")
async def subscribe_push(req: PushSubscriptionRequest, request: Request):
    user_id = _require_user_id(request)
    subscription = db.add_push_subscription(
        user_id=user_id,
        provider=req.provider,
        endpoint=req.endpoint,
        p256dh=req.p256dh,
        auth=req.auth,
        fcm_token=req.fcm_token,
        user_agent=req.user_agent,
    )
    return {"success": True, "subscription": subscription, "subscriptions": db.get_push_subscriptions(user_id)}


@app.get("/api/v1/push/subscriptions")
async def list_push_subscriptions(request: Request):
    user_id = _require_user_id(request)
    return {"subscriptions": db.get_push_subscriptions(user_id)}


@app.post("/api/v1/push/test")
async def test_push_delivery(request: Request):
    user_id = _require_user_id(request)
    test_alert = {
        "id": f"test-{uuid.uuid4()}",
        "user_id": user_id,
        "scheme_name": "Test Scheme",
        "channel": "push",
        "next_deadline": datetime.now().date().isoformat(),
        "last_checked": datetime.now().isoformat(),
        "contact": "test-contact",
    }
    result = dispatch_alert(test_alert)
    return {"success": bool(result.get("success")), "result": result}


@app.post("/api/v1/alerts/dispatch")
async def dispatch_all_alerts(request: Request):
    user_id = _require_user_id(request)
    outcome = _enqueue_or_run("process_deadline_alerts", {"user_id": user_id})
    db.track_feature_usage("dispatch_alerts", user_id=user_id, success=True, metadata={"mode": outcome.get("mode")})
    return {"success": True, **outcome}


@app.post("/api/v1/saved-schemes/status/poll")
async def poll_saved_scheme_statuses(request: Request):
    user_id = _require_user_id(request)
    outcome = _enqueue_or_run("poll_scheme_statuses", {"user_id": user_id})
    return {"success": True, **outcome}


@app.post("/api/v1/alerts/subscriptions/{alert_id}")
async def update_alert(alert_id: str, payload: Dict[str, Any], request: Request):
    user_id = _require_user_id(request)
    user_alerts = {a["id"]: a for a in db.get_alert_subscriptions(user_id)}
    if alert_id not in user_alerts:
        raise HTTPException(status_code=404, detail="Alert not found")
    is_active = payload.get("is_active")
    next_deadline = payload.get("next_deadline")
    ok = db.update_alert_subscription(alert_id, is_active=is_active, next_deadline=next_deadline)
    return {"success": ok, "alerts": db.get_alert_subscriptions(user_id)}


@app.post("/api/v1/admin/alerts/dispatch")
async def dispatch_all_alerts_admin(
    _: Dict[str, Any] = Depends(require_role(Role.ADMIN)),
    payload: Optional[AdminDispatchRequest] = None,
):
    outcome = _enqueue_or_run("process_deadline_alerts", {})
    return {"success": True, **outcome}


@app.post("/api/v1/schemes/search")
async def search_schemes(req: SchemeSearchRequest):
    cache_key = _cache_key("scheme_search", {"query": req.query, "limit": req.limit})
    cached = _cache_get(cache_key)
    if cached is not None:
        db.track_feature_usage("scheme_search", success=True, metadata={"cached": True})
        return cached

    docs = retriever.search(req.query, k=max(6, req.limit))
    catalog = _build_scheme_catalog(req.query)
    fuzzy_hits = difflib.get_close_matches(req.query, catalog, n=req.limit, cutoff=0.45)

    rows: List[Dict[str, Any]] = []
    seen = set()
    for name in fuzzy_hits:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "scheme_name": name,
                "source": "catalog_fuzzy",
                "relevance": 0.7,
            }
        )

    for doc in docs:
        md = doc.metadata or {}
        name = _first_non_empty(md, ["scheme_name", "title"], "")
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        snippet = str(doc.page_content or "").replace("\n", " ").strip()[:180]
        rows.append(
            {
                "scheme_name": name,
                "eligibility": _first_non_empty(md, ["eligibility"], "Not specified"),
                "benefits": _first_non_empty(md, ["benefits"], "Not specified"),
                "snippet": snippet + ("..." if len(str(doc.page_content or "")) > 180 else ""),
                "source": "retriever",
                "relevance": float(md.get("match_confidence") or 0.5),
            }
        )
        if len(rows) >= req.limit:
            break

    response = {"query": req.query, "results": rows[: req.limit]}
    _cache_set(cache_key, response)
    db.track_feature_usage("scheme_search", success=True, metadata={"cached": False, "results": len(response["results"])})
    return response


@app.get("/api/v1/schemes/autosuggest")
async def autosuggest_schemes(q: str, limit: int = 8):
    query = q.strip()
    if len(query) < 2:
        return {"query": query, "suggestions": []}
    safe_limit = max(1, min(limit, 15))
    cache_key = _cache_key("autosuggest", {"q": query, "limit": safe_limit})
    cached = _cache_get(cache_key)
    if cached is not None:
        db.track_feature_usage("autosuggest", success=True, metadata={"cached": True})
        return cached
    catalog = _build_scheme_catalog(query)
    query_lower = query.lower()

    prefix = [name for name in catalog if name.lower().startswith(query_lower)]
    contains = [name for name in catalog if query_lower in name.lower() and name not in prefix]
    fuzzy = difflib.get_close_matches(query, catalog, n=safe_limit * 2, cutoff=0.45)

    merged: List[str] = []
    for name in prefix + contains + fuzzy:
        if name not in merged:
            merged.append(name)
        if len(merged) >= safe_limit:
            break
    response = {"query": query, "suggestions": merged}
    _cache_set(cache_key, response)
    db.track_feature_usage("autosuggest", success=True, metadata={"cached": False, "count": len(merged)})
    return response


@app.post("/api/v1/schemes/compare")
async def compare_schemes(req: SchemeCompareRequest):
    cleaned = [str(name or "").strip() for name in req.scheme_names if str(name or "").strip()]
    if len(cleaned) < 2 or len(cleaned) > 3:
        db.track_feature_usage("scheme_compare", success=False, metadata={"reason": "invalid_length"})
        raise HTTPException(status_code=400, detail="Comparison requires 2 to 3 non-empty scheme names")
    if len({name.lower() for name in cleaned}) != len(cleaned):
        db.track_feature_usage("scheme_compare", success=False, metadata={"reason": "duplicates"})
        raise HTTPException(status_code=400, detail="Comparison requires unique scheme names")

    rows: List[Dict[str, Any]] = []
    for scheme_name in cleaned:
        local_query = " | ".join([
            scheme_name,
            f"state: {req.state}" if req.state else "",
            f"district: {req.district}" if req.district else "",
            f"pincode: {req.pincode}" if req.pincode else ""
        ]).strip(" |")
        docs = retriever.search(local_query, k=8)

        selected = None
        best_score = -1.0
        for doc in docs:
            title = str(doc.metadata.get("scheme_name") or doc.metadata.get("title") or "")
            title_norm = _normalize_scheme_name(title)
            query_norm = _normalize_scheme_name(scheme_name)
            if query_norm and (query_norm in title_norm or title_norm in query_norm):
                score = 1.0
            else:
                score = _token_overlap_score(title, scheme_name)
            if score > best_score:
                best_score = score
                selected = doc

        if not selected or best_score < 0.2:
            rows.append({
                "scheme_name": scheme_name,
                "eligibility": "Not clearly available in current sources",
                "benefits": "Not clearly available in current sources",
                "documents": "Not clearly available in current sources",
                "deadline": "Not specified",
                "health_score": {"score": 35, "confidence_score": 0, "freshness_score": 50, "source_quality_score": 50}
            })
            continue
        md = selected.metadata
        rows.append({
            "scheme_name": _first_non_empty(md, ["scheme_name", "title"], scheme_name),
            "eligibility": _first_non_empty(md, ["eligibility", "eligibility_summary"], "Not specified"),
            "benefits": _first_non_empty(md, ["benefits"], "Not specified"),
            "documents": _first_non_empty(md, ["documents_required", "documents"], "Not specified"),
            "deadline": _first_non_empty(md, ["deadline", "last_date"], "Not specified"),
            "apply_link": _first_non_empty(md, ["apply_link", "official_site", "url"], "Not specified"),
            "health_score": compute_scheme_health_score(md),
        })
    db.track_feature_usage("scheme_compare", success=True, metadata={"count": len(cleaned)})
    return {"comparison": rows, "generated_at": datetime.now().isoformat()}


@app.post("/api/v1/checklists/generate")
async def generate_checklist(req: ChecklistRequest, request: Request):
    user_id = _require_user_id(request)
    docs = retriever.search(req.scheme_name, k=4)
    items: List[Dict[str, Any]] = req.items or []
    if not items and docs:
        items = build_checklist_items_from_doc(docs[0])
    payload = db.save_checklist(user_id, req.scheme_name, items)
    return {"success": True, "checklist": payload}


@app.get("/api/v1/checklists/{scheme_name}")
async def get_checklist(scheme_name: str, request: Request):
    user_id = _require_user_id(request)
    checklist = db.get_checklist(user_id, scheme_name)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return checklist


@app.post("/api/v1/checklists/{scheme_name}")
async def update_checklist(scheme_name: str, req: ChecklistRequest, request: Request):
    user_id = _require_user_id(request)
    items = req.items or []
    payload = db.save_checklist(user_id, scheme_name, items)
    return {"success": True, "checklist": payload}


@app.post("/api/v1/prefill")
async def generate_prefill(req: PrefillRequest, request: Request):
    user_id = _require_user_id(request)
    profile = req.profile_data or db.get_user_profile_for_chat(user_id) or {}
    ocr_fields = req.ocr_fields or {}
    merged = {}
    key_map = [
        "name", "gender", "age", "state", "district", "pincode", "category",
        "annual_income", "family_income", "employment_status"
    ]
    for key in key_map:
        merged[key] = ocr_fields.get(key) if ocr_fields.get(key) not in [None, ""] else profile.get(key)
    merged["generated_for_scheme"] = req.scheme_name
    merged["generated_at"] = datetime.now().isoformat()
    return {"prefill_sheet": merged}


@app.get("/api/v1/family/members")
async def list_family_members(request: Request):
    user_id = _require_user_id(request)
    return {"members": db.get_family_members(user_id)}


@app.post("/api/v1/family/members")
async def create_family_member(req: FamilyMemberRequest, request: Request):
    user_id = _require_user_id(request)
    member = db.add_family_member(user_id, req.model_dump())
    return {"success": True, "member": member, "members": db.get_family_members(user_id)}


@app.delete("/api/v1/family/members/{member_id}")
async def remove_family_member(member_id: str, request: Request):
    user_id = _require_user_id(request)
    ok = db.delete_family_member(user_id, member_id)
    return {"success": ok, "members": db.get_family_members(user_id)}


@app.get("/api/v1/family/eligibility")
async def family_eligibility(request: Request):
    user_id = _require_user_id(request)
    primary = db.get_user_profile_for_chat(user_id) or {}
    members = db.get_family_members(user_id)
    profiles = [{"name": primary.get("name") or "Primary", **primary}] + members
    results = []
    for profile in profiles[:8]:
        docs = retriever.search_by_profile(profile, query="family eligibility", k=4)
        top = []
        for doc in docs[:3]:
            title = _first_non_empty(doc.metadata, ["scheme_name", "title"], "Unknown Scheme")
            eligible, confidence, _ = SchemeMatcher.check_eligibility_match(profile, doc.metadata)
            top.append({
                "scheme_name": title,
                "is_eligible": eligible,
                "confidence": round(confidence, 3)
            })
        results.append({"person": profile.get("name", "Member"), "recommendations": top})
    return {"family_results": results}


@app.post("/api/v1/eligibility/simulate")
async def simulate_eligibility(req: EligibilitySimulationRequest, request: Request):
    user_id = _require_user_id(request)
    base_profile = db.get_user_profile_for_chat(user_id) or {}
    simulated_profile = {**base_profile, **req.overrides}
    docs = retriever.search_by_profile(simulated_profile, query="eligibility simulation", k=max(3, min(req.top_k, 8)))
    results = []
    for doc in docs:
        title = _first_non_empty(doc.metadata, ["scheme_name", "title"], "Unknown Scheme")
        is_eligible, confidence, reasons = SchemeMatcher.check_eligibility_match(simulated_profile, doc.metadata)
        results.append({
            "scheme_name": title,
            "is_eligible": is_eligible,
            "confidence": round(confidence, 3),
            "reasons": reasons[:4],
            "health_score": compute_scheme_health_score(doc.metadata)
        })
    return {
        "base_profile": base_profile,
        "simulated_profile": simulated_profile,
        "results": results
    }


@app.post("/api/v1/schemes/rejection-explainer")
async def explain_rejection(req: RejectionExplainRequest, request: Request):
    user_id = _require_user_id(request)
    profile = db.get_user_profile_for_chat(user_id) or {}
    docs = retriever.search(req.scheme_name, k=5)
    target_doc = docs[0] if docs else None
    if target_doc is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    is_eligible, confidence, reasons = SchemeMatcher.check_eligibility_match(profile, target_doc.metadata)
    missing = [r for r in reasons if "⛔" in r or "⚠️" in r]
    suggestions = []
    for reason in missing[:4]:
        if "State" in reason:
            suggestions.append("Try schemes that match your state or update profile state if needed.")
        elif "Income" in reason:
            suggestions.append("Check income threshold variants or alternative schemes with higher caps.")
        elif "Age" in reason:
            suggestions.append("Look for schemes targeting your age group.")
        elif "Student" in reason:
            suggestions.append("Upload student proof if applicable or search non-student schemes.")
        else:
            suggestions.append("Review eligibility wording and provide missing profile documents.")
    return {
        "scheme_name": _first_non_empty(target_doc.metadata, ["scheme_name", "title"], req.scheme_name),
        "is_eligible": is_eligible,
        "confidence": round(confidence, 3),
        "missing_conditions": missing,
        "fix_suggestions": suggestions
    }


@app.post("/api/v1/scheme-lock")
async def set_scheme_lock(req: SchemeLockRequest, request: Request):
    user_id = _require_user_id(request)
    db.set_scheme_lock(user_id=user_id, scheme_name=req.scheme_name, locked=req.is_locked)
    return {"success": True, "scheme_lock": db.get_scheme_lock(user_id)}


@app.get("/api/v1/scheme-lock")
async def get_scheme_lock(request: Request):
    user_id = _require_user_id(request)
    return {"scheme_lock": db.get_scheme_lock(user_id)}


@app.get("/api/v1/offline-faq-pack")
async def get_offline_pack(request: Request):
    user_id = _require_user_id(request)
    existing = db.get_offline_faq_pack(user_id)
    if existing:
        return existing
    docs = retriever.search("top government schemes FAQ eligibility documents", k=8)
    faq = []
    for doc in docs:
        md = doc.metadata or {}
        faq.append({
            "scheme_name": _first_non_empty(md, ["scheme_name", "title"], "Scheme"),
            "faq": [
                {"q": "Who is eligible?", "a": _first_non_empty(md, ["eligibility"], "Refer official criteria.")},
                {"q": "Which documents are needed?", "a": _first_non_empty(md, ["documents_required", "documents"], "Refer official documents list.")},
                {"q": "How to apply?", "a": _first_non_empty(md, ["application_process"], "Apply through official portal or office.")}
            ],
            "source": _first_non_empty(md, ["official_site", "apply_link", "source"], "myscheme.gov.in")
        })
    pack = {"generated_at": datetime.now().isoformat(), "items": faq}
    db.save_offline_faq_pack(user_id, pack)
    return pack


@app.get("/api/v1/admin/ingestion-health")
async def admin_ingestion_health(_: Dict[str, Any] = Depends(require_role(Role.ADMIN))):
    metrics = db.get_admin_ingestion_metrics()
    if not metrics:
        # Seed default row so UI always has data.
        db.upsert_admin_ingestion_metrics(
            source_name="myscheme.gov.in",
            total_schemes=0,
            parser_confidence=0.0,
            broken_links=0,
            pending_approvals=0,
            published_count=0
        )
        metrics = db.get_admin_ingestion_metrics()
    freshness_summary = {
        "latest_run_at": metrics[0]["last_run_at"] if metrics else None,
        "sources_monitored": len(metrics)
    }
    return {"freshness": freshness_summary, "rows": metrics}


@app.post("/api/v1/admin/ingestion-health")
async def admin_ingestion_health_upsert(
    payload: Dict[str, Any],
    _: Dict[str, Any] = Depends(require_role(Role.ADMIN)),
):
    db.upsert_admin_ingestion_metrics(
        source_name=str(payload.get("source_name") or "myscheme.gov.in"),
        total_schemes=int(payload.get("total_schemes") or 0),
        parser_confidence=float(payload.get("parser_confidence") or 0.0),
        broken_links=int(payload.get("broken_links") or 0),
        pending_approvals=int(payload.get("pending_approvals") or 0),
        published_count=int(payload.get("published_count") or 0),
    )
    return {"success": True, "rows": db.get_admin_ingestion_metrics()}


@app.get("/api/v1/admin/tasks/failures")
async def admin_task_failures(_: Dict[str, Any] = Depends(require_role(Role.ADMIN))):
    return {"failures": db.get_task_failures(limit=200)}


@app.get("/api/v1/admin/analytics")
async def admin_analytics(_: Dict[str, Any] = Depends(require_role(Role.ADMIN))):
    return {"analytics": db.get_admin_analytics_summary(), "generated_at": datetime.now().isoformat()}


# ============ Intent Detection for Conversational Flow ============
GREETING_PATTERNS = [
    "hi", "hello", "hey", "hii", "hiii", "namaste", "namaskar", "good morning",
    "good afternoon", "good evening", "howdy", "greetings", "sup", "yo",
    "thanks", "thank you", "धन्यवाद", "शुक्रिया", "नमस्ते", "नमस्कार",
    "ಹಲೋ", "வணக்கம்", "నమస్తే", "হ্যালো", "ਸਤ ਸ੍ਰੀ ਅਕਾਲ"
]

def detect_intent(message: str) -> str:
    """Detect the intent of the user message."""
    msg_lower = message.strip().lower()
    normalized = re.sub(r"[^a-z0-9\s]", "", msg_lower).strip()

    help_patterns = [
        "help", "what can you do", "what do you do", "how to use",
        "how does this work", "what is this", "support"
    ]
    if normalized in {"help", "what can you do", "how to use", "how does this work", "what is this"}:
        return "help"
    if any(p in normalized for p in help_patterns):
        return "help"
    
    # General conversation patterns (Prioritize over greetings)
    general_patterns = [
        "who are you", "what is your name", "who made you",
        "how are you", "what's up", "good morning", "good night",
        "tell me a joke", "say something", "talk to me", "are you real",
        "human", "robot", "bot", "ai", "intelligence", "smart",
        "what time", "what date", "current time", "today", "weather",
        "where are you", "location", "cool", "nice", "ok", "okay",
        "meaning of life", "love", "hate", "food", "eat", "drink"
    ]
    if any(p in msg_lower for p in general_patterns):
        return "general_chat"

    if len(msg_lower) < 15 and any(g in msg_lower for g in GREETING_PATTERNS[:14]):
        return "greeting"
    
    if any(t in msg_lower for t in ["thank", "thanks", "धन्यवाद", "शुक्रिया"]):
        return "thanks"

    detail_patterns = [
        "tell me more about", "tell me about", "more about", "details about",
        "more info on", "more information about", "explain", "what is the",
        "describe", "elaborate on", "info about", "information on",
        "details of", "scheme for", "yojana"
    ]
    if any(pattern in msg_lower for pattern in detail_patterns):
        return "scheme_detail"
    
    word_count = len(message.split())
    if 3 <= word_count <= 15 and message[0].isupper():
        if any(w in msg_lower for w in ["scheme", "yojana", "mission", "program", "fund", "allowance", "subsidy"]):
            return "scheme_detail"
            
    return "scheme_query"


GUEST_INTENT_MENU = (
    "Choose one option to continue:\n"
    "- 🔍 Search schemes by keyword\n"
    "- 🧭 Explore by category (Education, Health, Farmer, Women, Business)\n"
    "- 📋 Quick eligibility check (basic)"
)


def parse_guest_slots(history: List[Dict[str, str]], message: str) -> Dict[str, Optional[str]]:
    """Extract lightweight guest slots from chat text."""
    text_parts = [message]
    for item in history[-8:]:
        if item.get("role") == "user" and item.get("content"):
            text_parts.append(item["content"])
    text = " ".join(text_parts).lower()

    slots: Dict[str, Optional[str]] = {
        "age_range": None,
        "state": None,
        "gender": None,
        "occupation": None,
        "income_range": None,
    }

    age_match = re.search(r"\b(\d{1,2})\b", text)
    if age_match:
        age = int(age_match.group(1))
        if age < 18:
            slots["age_range"] = "Under 18"
        elif age <= 35:
            slots["age_range"] = "18-35"
        elif age <= 60:
            slots["age_range"] = "36-60"
        else:
            slots["age_range"] = "60+"

    state_match = re.search(
        r"\b(andhra pradesh|arunachal pradesh|assam|bihar|chhattisgarh|goa|gujarat|haryana|himachal pradesh|jharkhand|karnataka|kerala|madhya pradesh|maharashtra|manipur|meghalaya|mizoram|nagaland|odisha|punjab|rajasthan|sikkim|tamil nadu|telangana|tripura|uttar pradesh|uttarakhand|west bengal|delhi|chandigarh|puducherry)\b",
        text
    )
    if state_match:
        slots["state"] = state_match.group(1).title()

    for g in ["female", "male", "transgender", "woman", "man", "girl", "boy"]:
        if g in text:
            slots["gender"] = "Female" if g in ["female", "woman", "girl"] else ("Male" if g in ["male", "man", "boy"] else "Transgender")
            break

    occupation_map = {
        "student": "Student",
        "farmer": "Farmer",
        "worker": "Worker",
        "labour": "Worker",
        "labor": "Worker",
        "business": "Business",
        "self employed": "Business",
        "entrepreneur": "Business",
        "unemployed": "Unemployed",
    }
    for key, value in occupation_map.items():
        if key in text:
            slots["occupation"] = value
            break

    income_match = re.search(r"(income|salary|earn).{0,18}(\d{4,8})", text)
    if income_match:
        income = int(income_match.group(2))
        if income < 200000:
            slots["income_range"] = "Below 2L"
        elif income <= 800000:
            slots["income_range"] = "2L-8L"
        else:
            slots["income_range"] = "Above 8L"
    elif "low income" in text or "bpl" in text:
        slots["income_range"] = "Below 2L"
    elif "middle income" in text:
        slots["income_range"] = "2L-8L"

    return slots


def missing_guest_essentials(slots: Dict[str, Optional[str]]) -> List[str]:
    missing = []
    if not slots.get("age_range"):
        missing.append("age_range")
    if not slots.get("state"):
        missing.append("state")
    if not slots.get("occupation"):
        missing.append("occupation")
    return missing


def next_guest_question(slot_key: str) -> str:
    if slot_key == "age_range":
        return "Before I suggest schemes, what is your age range? (Under 18 / 18-35 / 36-60 / 60+)"
    if slot_key == "state":
        return "Which state do you live in?"
    if slot_key == "occupation":
        return "Which best describes you: Student, Farmer, Worker, Business, or Unemployed?"
    return "Please share one more detail to continue."


def append_signed_in_actions(reply: str, user_profile: Dict[str, Any], user_id: Optional[str]) -> str:
    missing_fields = []
    for field in ["state", "age", "employment_status", "annual_income", "category"]:
        if not user_profile.get(field):
            missing_fields.append(field)

    actions = [
        "Smart actions: Save scheme | Set reminder | Upload documents (OCR) | Track application status"
    ]
    if missing_fields:
        readable = ", ".join(missing_fields[:3])
        actions.append(
            f"Profile tip: Adding {readable} will improve eligibility accuracy. You can update profile now."
        )

    if user_id:
        alerts_on = db.get_alert_preference(user_id)
        actions.append(
            "Updates: Alerts are ON for new matching schemes and rule changes."
            if alerts_on else
            "Updates: Say 'notify me about new schemes' to enable alerts."
        )
    return reply.rstrip() + "\n\n" + "\n".join(actions)


def rank_docs_for_signed_in(user_profile: Dict[str, Any], documents: List[Any], limit: int = 8) -> List[Any]:
    """Attach eligibility metadata and rank docs across eligible/possible/ineligible."""
    ranked: List[Any] = []
    seen_titles = set()
    for doc in documents:
        title = doc.metadata.get("scheme_name") or doc.metadata.get("title") or "Unknown Scheme"
        normalized = str(title).strip().lower()
        if normalized in seen_titles:
            continue
        seen_titles.add(normalized)

        is_eligible, confidence, reasons = SchemeMatcher.check_eligibility_match(user_profile, doc.metadata)
        doc.metadata["eligibility_reasons"] = "\n".join(reasons) if reasons else "No automated checks performed."
        doc.metadata["match_confidence"] = confidence

        # Tiered ranking: eligible first, then possible, then ineligible.
        if is_eligible and confidence >= 0.75:
            score = 3.0 + confidence
        elif is_eligible:
            score = 2.0 + confidence
        else:
            score = 1.0
        ranked.append((score, doc))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in ranked[:limit]]


def extract_last_scheme_from_history(history: List[Dict[str, str]]) -> Optional[str]:
    """Try to recover the most recently discussed scheme name from assistant replies."""
    for item in reversed(history[-12:]):
        if item.get("role") != "assistant":
            continue
        text = item.get("content") or ""
        # Common formats in this app:
        # 1) "### Scheme Name"
        # 2) "**[Scheme Name]**"
        m_heading = re.search(r"^###\s+([^\n]+)", text, flags=re.MULTILINE)
        if m_heading:
            return m_heading.group(1).strip()
        m_bracket = re.search(r"\*\*\[([^\]]+)\]\*\*", text)
        if m_bracket:
            return m_bracket.group(1).strip()
    return None


def promote_scheme_first(documents: List[Any], scheme_name: Optional[str]) -> List[Any]:
    if not scheme_name:
        return documents
    target = scheme_name.lower()
    prioritized = []
    others = []
    for doc in documents:
        title = str(doc.metadata.get("scheme_name") or doc.metadata.get("title") or "").lower()
        if target in title or title in target:
            prioritized.append(doc)
        else:
            others.append(doc)
    return prioritized + others


def extract_scheme_focus_from_text(text: str) -> Optional[str]:
    """Extract an explicit scheme mention from user text when possible."""
    lower = text.lower()
    # Known high-frequency explicit mention.
    if "pm kisan" in lower:
        return "PM Kisan"

    patterns = [
        r"(?:about|for|regarding)\s+([a-z0-9&()'\/\-\s]{4,80})",
        r"(?:eligible for|apply for|details of)\s+([a-z0-9&()'\/\-\s]{4,80})",
    ]
    for pattern in patterns:
        m = re.search(pattern, lower)
        if not m:
            continue
        candidate = m.group(1).strip(" .?!,:;")
        # Trim common trailing phrases.
        candidate = re.sub(r"\b(please|now|today|for me|in my state)\b.*$", "", candidate).strip()
        if len(candidate) >= 4 and candidate not in {"schemes", "scheme"}:
            return " ".join(w.capitalize() for w in candidate.split())
    return None


def extract_recent_scheme_focus(history: List[Dict[str, str]]) -> Optional[str]:
    """Look back in user history for the latest explicit scheme mention."""
    for item in reversed(history[-12:]):
        if item.get("role") != "user":
            continue
        content = item.get("content") or ""
        scheme = extract_scheme_focus_from_text(content)
        if scheme:
            return scheme
    return None


def filter_docs_for_scheme_focus(documents: List[Any], scheme_name: Optional[str], strict: bool = False) -> List[Any]:
    """Keep docs closely matching the scheme focus."""
    if not scheme_name:
        return documents
    focus = scheme_name.lower()
    focus_tokens = [t for t in re.split(r"[^a-z0-9]+", focus) if len(t) >= 2]
    matched = []
    for doc in documents:
        title = str(doc.metadata.get("scheme_name") or doc.metadata.get("title") or "").lower()
        if focus in title or title in focus:
            matched.append(doc)
            continue
        if strict:
            # For explicit scheme lookups, all focus tokens should appear.
            if focus_tokens and all(t in title for t in focus_tokens):
                matched.append(doc)
            continue
        # Non-strict overlap fallback for continuity scenarios.
        overlap = sum(1 for t in focus_tokens if t in title)
        if overlap >= max(1, min(2, len(focus_tokens))):
            matched.append(doc)
    return matched


def _safe_text(value: Any, fallback: str = "Not specified") -> str:
    if value is None:
        return fallback
    txt = str(value).strip()
    if not txt:
        return fallback
    return txt


def _first_non_empty(metadata: Dict[str, Any], keys: List[str], fallback: str = "Not specified") -> str:
    for key in keys:
        value = metadata.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return fallback


def compute_scheme_health_score(metadata: Dict[str, Any]) -> Dict[str, Any]:
    confidence = float(metadata.get("match_confidence") or 0.0)
    confidence_score = max(0, min(100, int(confidence * 100)))
    freshness_score = 90 if metadata.get("last_checked") else 65
    source_quality = 90 if metadata.get("official_site") or metadata.get("apply_link") else 55
    total = int(round((0.45 * confidence_score) + (0.3 * freshness_score) + (0.25 * source_quality)))
    return {
        "score": total,
        "confidence_score": confidence_score,
        "freshness_score": freshness_score,
        "source_quality_score": source_quality,
    }


def build_source_citations(documents: List[Any], limit: int = 5) -> List[Dict[str, Any]]:
    citations: List[Dict[str, Any]] = []
    for doc in documents[:limit]:
        md = doc.metadata or {}
        source = _first_non_empty(md, ["source", "government", "department"], "myscheme.gov.in")
        section = _first_non_empty(md, ["category", "beneficiary_type", "title"], "Scheme details")
        content = str(doc.page_content or "").replace("\n", " ").strip()
        snippet = content[:220] + ("..." if len(content) > 220 else "")
        url = _first_non_empty(md, ["official_site", "apply_link", "url"], "")
        citations.append({
            "scheme_name": _first_non_empty(md, ["scheme_name", "title"], "Unknown Scheme"),
            "document": source,
            "section": section,
            "snippet": snippet,
            "url": url if url.lower().startswith("http") else None,
            "health_score": compute_scheme_health_score(md),
        })
    return citations


def build_checklist_items_from_doc(doc: Any) -> List[Dict[str, Any]]:
    md = doc.metadata or {}
    items: List[Dict[str, Any]] = []
    documents = _first_non_empty(md, ["documents_required", "documents", "required_documents"], "")
    if documents and documents != "Not specified":
        for idx, item in enumerate(re.split(r"[,;\n•]+", documents)):
            title = item.strip(" -")
            if not title:
                continue
            items.append({
                "id": f"doc-{idx+1}",
                "title": f"Prepare: {title}",
                "completed": False,
                "type": "document"
            })
    application = _first_non_empty(md, ["application_process"], "")
    if application and application != "Not specified":
        for idx, line in enumerate(re.split(r"[\n]+", application)):
            step = line.strip(" -*")
            if len(step) < 4:
                continue
            items.append({
                "id": f"step-{idx+1}",
                "title": step,
                "completed": False,
                "type": "application_step"
            })
    if not items:
        items = [
            {"id": "step-1", "title": "Confirm eligibility conditions", "completed": False, "type": "application_step"},
            {"id": "step-2", "title": "Collect required identity and income documents", "completed": False, "type": "document"},
            {"id": "step-3", "title": "Submit application through official portal or office", "completed": False, "type": "application_step"},
        ]
    return items[:20]


def _normalize_scheme_name(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", str(text).lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _token_overlap_score(a: str, b: str) -> float:
    a_tokens = {t for t in _normalize_scheme_name(a).split() if len(t) >= 2}
    b_tokens = {t for t in _normalize_scheme_name(b).split() if len(t) >= 2}
    if not a_tokens or not b_tokens:
        return 0.0
    inter = len(a_tokens.intersection(b_tokens))
    return inter / max(len(a_tokens), len(b_tokens))


def _extract_catalog_names_from_json(value: Any) -> List[str]:
    names: List[str] = []
    if isinstance(value, dict):
        for key in ["scheme_name", "title", "name"]:
            raw = str(value.get(key) or "").strip()
            if raw:
                names.append(raw)
                break
        for nested in value.values():
            names.extend(_extract_catalog_names_from_json(nested))
    elif isinstance(value, list):
        for item in value:
            names.extend(_extract_catalog_names_from_json(item))
    return names


def _build_scheme_catalog(query_hint: Optional[str] = None) -> List[str]:
    cache_key = _cache_key("scheme_catalog", {"hint": query_hint or ""})
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    catalog = set()

    data_dir = os.path.join(BASE_DIR, "backend", "data", "schemes_json")
    if os.path.isdir(data_dir):
        for file_name in os.listdir(data_dir):
            if not file_name.endswith(".json"):
                continue
            path = os.path.join(data_dir, file_name)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                for name in _extract_catalog_names_from_json(data):
                    catalog.add(name)
            except Exception:
                continue

    for seed in [query_hint or "government scheme", "PM Kisan", "pension scholarship loan"]:
        docs = retriever.search(seed, k=20)
        for doc in docs:
            title = _first_non_empty(doc.metadata or {}, ["scheme_name", "title"], "")
            if title:
                catalog.add(title)

    if not catalog:
        catalog.update({"PM Kisan", "Atal Pension Yojana", "Mudra Loan"})

    result = sorted(catalog)
    _cache_set(cache_key, result, ttl=60)
    return result


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, req: ChatRequest):
    """
    Chat with the assistant about government schemes
    Supports all Indic languages with automatic translation
    """
    try:
        original_message = req.message
        detected_lang = None
        language_name = None
        locked_scheme_name: Optional[str] = None
        
        # Load user profile from database if user_id provided
        user_profile = req.user_profile
        if req.user_id and not user_profile:
            user_profile = db.get_user_profile_for_chat(req.user_id)
            if user_profile:
                logger.info(f"Loaded profile from database for user: {req.user_id}")
        if req.user_id:
            lock_state = db.get_scheme_lock(req.user_id)
            if lock_state.get("is_locked"):
                locked_scheme_name = lock_state.get("scheme_name")
        if req.scheme_lock:
            locked_scheme_name = req.scheme_lock
        
        # Load chat history from database if user_id provided
        db_chat_history = []
        if req.user_id:
            db_chat_history = db.get_chat_history(req.user_id)
        
        # Merge chat history
        merged_history = req.history or []
        if db_chat_history:
            for entry in db_chat_history[-10:]:
                merged_history.append({"role": "user", "content": entry["question"]})
                merged_history.append({"role": "assistant", "content": entry["answer"]})
        
        # Step 1: Detect or validate source language
        if req.source_lang is None or req.source_lang == "auto":
            detected_lang = translator.detect_language_code(req.message)
            if detected_lang is None:
                detected_lang = "en_XX"
            source_lang = detected_lang
        else:
            source_lang = req.source_lang
            detected_lang = source_lang
        
        target_lang = req.target_lang if req.target_lang else source_lang
        language_name = translator.SUPPORTED_LANGUAGES.get(detected_lang, "Unknown")
        
        # Step 2: Translate to English if needed (for RAG retrieval)
        if source_lang != "en_XX":
            english_message = translator.to_english(req.message, source_lang=source_lang)
            logger.info(f"Translated query: {english_message}")
        else:
            english_message = req.message
        
        # Step 2.5: Intent Detection - Handle greetings/thanks without RAG
        intent = detect_intent(english_message)

        lowered_message = english_message.lower().strip()

        def localized_reply(text: str) -> str:
            if target_lang != "en_XX":
                return translator.from_english(text, target_lang)
            return text

        # Signed-in smart action commands
        if req.user_id and user_profile:
            if lowered_message.startswith("save scheme"):
                scheme = english_message.split("save scheme", 1)[-1].strip(" :.-")
                if not scheme:
                    return ChatResponse(reply=localized_reply("Please specify a scheme name, for example: Save scheme PM Kisan"), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)
                db.save_scheme(req.user_id, scheme)
                return ChatResponse(reply=localized_reply(f"Saved '{scheme}' to your profile list."), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)
            if lowered_message.startswith("set reminder"):
                db.add_reminder(req.user_id, english_message)
                return ChatResponse(reply=localized_reply("Reminder saved. I will keep this in your reminders list."), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)
            if "notify me about new schemes" in lowered_message:
                db.set_alert_preference(req.user_id, True)
                return ChatResponse(reply=localized_reply("Done. I will mark alerts as enabled for new matching schemes and rule updates."), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)
            if "stop scheme alerts" in lowered_message:
                db.set_alert_preference(req.user_id, False)
                return ChatResponse(reply=localized_reply("Alerts turned off. You can say 'notify me about new schemes' anytime to re-enable."), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)
            if "track application status" in lowered_message:
                return ChatResponse(reply=localized_reply("To track application status, share the scheme name and your application/reference number. I will guide the official tracking path."), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)
            if lowered_message.startswith("lock this scheme"):
                scheme = english_message.split("lock this scheme", 1)[-1].strip(" :.-")
                if not scheme:
                    return ChatResponse(reply=localized_reply("Please specify a scheme name to lock."), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)
                db.set_scheme_lock(req.user_id, scheme, True)
                return ChatResponse(reply=localized_reply(f"Scheme lock enabled for '{scheme}'. Follow-up questions will stay focused on this scheme."), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)
            if "unlock scheme" in lowered_message:
                db.set_scheme_lock(req.user_id, None, False)
                return ChatResponse(reply=localized_reply("Scheme lock disabled. I will use all relevant schemes again."), detected_language=detected_lang, language_name=language_name, original_message=original_message, translated_message=None)

        if intent == "greeting":
            if user_profile:
                first_name = str(user_profile.get("name") or "").split(" ")[0] or "there"
                reply = (
                    f"Welcome back, {first_name}. I have your profile details.\n"
                    "Want me to check schemes you are eligible for now?"
                )
            else:
                reply = (
                    "Hello! I can help you find government schemes and check basic eligibility. "
                    "For personalized results, you may sign in.\n\n"
                    f"{GUEST_INTENT_MENU}"
                )

            if target_lang != "en_XX":
                reply = translator.from_english(reply, target_lang)

            return ChatResponse(
                reply=reply, detected_language=detected_lang, language_name=language_name,
                original_message=original_message, translated_message=None
            )
        
        if intent == "thanks":
            reply = "You're welcome! Feel free to ask if you have more questions about government schemes."
            if target_lang != "en_XX":
                reply = translator.from_english(reply, target_lang)
            return ChatResponse(
                reply=reply, detected_language=detected_lang, language_name=language_name,
                original_message=original_message, translated_message=None
            )

        if intent == "help":
            if user_profile:
                reply = (
                    "I can help you with personalized scheme support:\n"
                    "- Check schemes you are eligible for\n"
                    "- Explain benefits, documents, and deadlines\n"
                    "- Show how to apply for a selected scheme\n"
                    "- Save schemes, set reminders, and track status guidance\n\n"
                    "Try: 'Show schemes for me' or 'How to apply for PM Kisan?'"
                )
            else:
                reply = (
                    "I can help you discover and understand government schemes.\n"
                    "- Search by keyword\n"
                    "- Explore by category\n"
                    "- Do a quick basic eligibility check\n\n"
                    "Sign in for precise personalized eligibility, saved schemes, and direct links."
                )
            if target_lang != "en_XX":
                reply = translator.from_english(reply, target_lang)
            return ChatResponse(
                reply=reply, detected_language=detected_lang, language_name=language_name,
                original_message=original_message, translated_message=None
            )

        if intent == "general_chat":
            if user_profile:
                first_name = str(user_profile.get("name") or "").split(" ")[0] or "there"
                reply = (
                    f"Welcome back, {first_name}. I can use your saved profile for exact eligibility checks.\n"
                    "Ask me things like:\n"
                    "- What am I eligible for?\n"
                    "- Show top schemes for me\n"
                    "- How to apply for PM Kisan"
                )
            else:
                reply = (
                    "I can help you explore schemes quickly in guest mode.\n"
                    f"{GUEST_INTENT_MENU}\n\n"
                    "For precise eligibility and saved actions, sign in."
                )
            if target_lang != "en_XX":
                reply = translator.from_english(reply, target_lang)
            return ChatResponse(
                reply=reply, detected_language=detected_lang, language_name=language_name,
                original_message=original_message, translated_message=None
            )
        
        # Step 3: Retrieve relevant documents (Smart Switching)
        # Note: The retriever now handles SchemeMatcher ranking internally
        if user_profile:
            logger.info(f"Searching with profile-aware matching for signed-in user: {req.user_id}")
            # If user shares incremental profile facts without naming a new scheme,
            # anchor retrieval to the previously discussed scheme for continuity.
            previous_scheme = extract_last_scheme_from_history(merged_history)
            explicit_scheme = extract_scheme_focus_from_text(english_message)
            recent_user_scheme = extract_recent_scheme_focus(merged_history)
            has_explicit_scheme_name = any(
                token in lowered_message for token in
                ["pm kisan", "yojana", "scheme", "loan", "pension", "scholarship"]
            )
            has_profile_update_facts = any(
                k in lowered_message for k in ["hectare", "land", "income", "age", "state", "category", "i have", "my"]
            )
            target_scheme = locked_scheme_name or explicit_scheme or recent_user_scheme or previous_scheme
            should_anchor_to_previous = bool(target_scheme) and (has_explicit_scheme_name or has_profile_update_facts)
            is_specific_scheme_query = bool(explicit_scheme) and any(
                k in lowered_message for k in [
                    "eligible", "eligibility", "how to apply", "apply", "benefit", "details", "tell me more", "about"
                ]
            )
            retrieval_query = (
                f"{english_message} for scheme focus {target_scheme}"
                if should_anchor_to_previous else english_message
            )
            if user_profile.get("district"):
                retrieval_query += f" | district: {user_profile.get('district')}"
            if user_profile.get("pincode"):
                retrieval_query += f" | pincode: {user_profile.get('pincode')}"

            # Combine semantic and profile-driven retrieval, then classify all into Eligible/Possible/Not Eligible.
            base_docs = retriever.search(retrieval_query, k=10)
            profile_seed_docs = retriever.search_by_profile(user_profile, query=retrieval_query, k=6)
            combined_docs = base_docs + profile_seed_docs
            if should_anchor_to_previous and target_scheme:
                anchor_docs = retriever.search(target_scheme, k=10)
                combined_docs = anchor_docs + combined_docs
            docs = rank_docs_for_signed_in(user_profile, combined_docs, limit=8)
            if should_anchor_to_previous:
                docs = promote_scheme_first(docs, target_scheme)
                strict_focus = bool(explicit_scheme or recent_user_scheme)
                focused = filter_docs_for_scheme_focus(docs, target_scheme, strict=strict_focus)
                if focused:
                    docs = focused[:5]
                elif has_profile_update_facts and target_scheme:
                    no_match_reply = (
                        f"I still could not find reliable context for '{target_scheme}' in the current database. "
                        "Please provide the exact scheme name again or ask for similar schemes in your category/state."
                    )
                    if target_lang != "en_XX":
                        no_match_reply = translator.from_english(no_match_reply, target_lang)
                    if req.user_id:
                        db.append_chat_entry(req.user_id, original_message, no_match_reply)
                    return ChatResponse(
                        reply=no_match_reply,
                        detected_language=detected_lang,
                        language_name=language_name,
                        original_message=original_message,
                        translated_message=english_message if source_lang != "en_XX" else None
                    )
            # If user explicitly asked about one scheme and it is not retrieved, don't drift to unrelated schemes.
            if is_specific_scheme_query and explicit_scheme:
                focused = filter_docs_for_scheme_focus(docs, explicit_scheme, strict=True)
                if focused:
                    docs = focused[:5]
                else:
                    no_match_reply = (
                        f"I could not find reliable context for '{explicit_scheme}' in the current database. "
                        "Try another scheme name or ask for similar schemes in your category/state."
                    )
                    if target_lang != "en_XX":
                        no_match_reply = translator.from_english(no_match_reply, target_lang)
                    if req.user_id:
                        db.append_chat_entry(req.user_id, original_message, no_match_reply)
                    return ChatResponse(
                        reply=no_match_reply,
                        detected_language=detected_lang,
                        language_name=language_name,
                        original_message=original_message,
                        translated_message=english_message if source_lang != "en_XX" else None
                    )
            if not docs:
                docs = base_docs[:6]
        else:
            # Guest flow: collect minimal details before broad matching.
            guest_slots = parse_guest_slots(merged_history, english_message)
            missing = missing_guest_essentials(guest_slots)

            asked_for_search = any(
                key in lowered_message for key in
                ["scheme", "yojana", "find", "search", "category", "eligible", "eligibility", "benefit", "scholarship", "loan"]
            )

            if missing and asked_for_search:
                question = next_guest_question(missing[0])
                prompt = (
                    f"{question}\n\n"
                    "I only need basic info: age range, state, and occupation. "
                    "Gender and income are optional."
                )
                if target_lang != "en_XX":
                    prompt = translator.from_english(prompt, target_lang)
                return ChatResponse(
                    reply=prompt,
                    detected_language=detected_lang,
                    language_name=language_name,
                    original_message=original_message,
                    translated_message=english_message if source_lang != "en_XX" else None
                )

            query_parts = [english_message]
            if guest_slots.get("state"):
                query_parts.append(f"state: {guest_slots['state']}")
            if guest_slots.get("occupation"):
                query_parts.append(f"occupation: {guest_slots['occupation']}")
            if guest_slots.get("age_range"):
                query_parts.append(f"age group: {guest_slots['age_range']}")
            if guest_slots.get("income_range"):
                query_parts.append(f"income: {guest_slots['income_range']}")
            guest_query = " | ".join(query_parts)
            docs = retriever.search(guest_query, k=6)

        source_citations = build_source_citations(docs)
        if source_citations:
            top_health = source_citations[0].get("health_score", {}).get("score", 0)
            reply_prefix = f"Scheme health score (top match): {top_health}/100\n\n"
        else:
            reply_prefix = ""

        # Pre-process documents to ensure LINKS from metadata are visible to the LLM
        # (generator.py's format_docs_for_context uses page_content)
        for doc in docs:
            official_site = doc.metadata.get("official_site")
            apply_link = doc.metadata.get("apply_link")
            
            links_block = []
            if official_site and str(official_site).lower() not in ["none", "nan", "ma", "not available", ""]:
                if "official website" not in doc.page_content.lower():
                    links_block.append(f"Official Website: {official_site}")
            
            if apply_link and str(apply_link).lower() not in ["none", "nan", "ma", "not available", ""]:
                if "apply online" not in doc.page_content.lower():
                    links_block.append(f"Apply Online: {apply_link}")
                
            if links_block:
                doc.page_content += "\n\n[SCHEME LINKS]:\n" + "\n".join(links_block)
            else:
                doc.page_content += "\n\n[SCHEME LINKS]:\nLinks Not Provided In Database"

        
        # Step 4: Generate answer
        # Changed: We now pass the List[Document] directly to the generator
        mode = "signed_in" if user_profile else "guest"
        reply = generate_answer(
            user_question=english_message,
            context_documents=docs,  # Updated Argument
            history=merged_history,
            user_profile=user_profile,
            mode=mode
        )

        if user_profile:
            reply = reply_prefix + append_signed_in_actions(reply, user_profile, req.user_id)
        else:
            reply = (
                reply_prefix + reply.rstrip() + "\n\n"
                "Sign in to save your profile, get precise eligibility, and receive direct application links.\n"
                "Next: Refine search | Explore another category | Sign in"
            )
        
        # Step 5: Translate response if needed
        if target_lang != "en_XX":
            reply = translator.from_english(reply, target_lang)
        
        # Save chat entry
        if req.user_id:
            db.append_chat_entry(req.user_id, original_message, reply)

        return ChatResponse(
            reply=reply,
            detected_language=detected_lang,
            language_name=language_name,
            original_message=original_message,
            translated_message=english_message if source_lang != "en_XX" else None,
            sources=source_citations
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/chat/multilingual")
async def multilingual_chat(
    message: str,
    auto_detect: bool = True,
    respond_in_same_language: bool = True
):
    """Simplified multilingual chat endpoint"""
    try:
        source_lang = translator.detect_language_code(message) if auto_detect else "en_XX"
        target_lang = source_lang if respond_in_same_language else "en_XX"
        
        req = ChatRequest(message=message, source_lang=source_lang, target_lang=target_lang)
        return await chat(req)
        
    except Exception as e:
        logger.error(f"Multilingual chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health/translator")
async def translator_health():
    """Check if translator is working"""
    try:
        test = translator.translate("नमस्ते", source_lang="hi_IN", target_lang="en_XX")
        return {
            "status": "healthy",
            "test_translation": test,
            "device": translator.device,
            "model": translator.model_name
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ---- WebSocket Chat Endpoint ---- #
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat responses."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            history = data.get("history", [])
            source_lang = data.get("source_lang", "auto")
            target_lang = data.get("target_lang", "en_XX")
            user_id = data.get("user_id")

            try:
                # Reuse the chat logic
                req = ChatRequest(
                    message=message,
                    history=history,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    user_id=user_id,
                )
                # Build a fake Request object for rate limiter compatibility
                import asyncio
                from unittest.mock import MagicMock
                fake_request = MagicMock()
                fake_request.client = MagicMock()
                fake_request.client.host = "127.0.0.1"

                # Use existing chat handler without rate limiter
                original_message = req.message
                detected_lang = None
                user_profile = None
                if req.user_id:
                    user_profile = db.get_user_profile_for_chat(req.user_id)

                if source_lang == "auto":
                    detected_lang = translator.detect_language_code(req.message) or "en_XX"
                else:
                    detected_lang = source_lang

                if detected_lang != "en_XX":
                    english_message = translator.to_english(req.message, source_lang=detected_lang)
                else:
                    english_message = req.message

                # RAG retrieval
                docs = retriever.search(english_message, k=5)
                context = "\n".join([doc.page_content for doc in docs]) if docs else ""

                # Generate reply
                import openai
                client_ai = openai.OpenAI()
                system_prompt = f"You are a helpful Indian government scheme assistant. Use the following context:\n{context}"
                messages_for_ai = [{"role": "system", "content": system_prompt}]
                for h in history[-6:]:
                    messages_for_ai.append({"role": h.get("role", "user"), "content": h.get("content", "")})
                messages_for_ai.append({"role": "user", "content": english_message})

                completion = client_ai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_for_ai,
                    stream=True,
                )

                full_reply = ""
                for chunk in completion:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_reply += delta.content
                        await websocket.send_json({"type": "chunk", "content": delta.content})

                # Translate back if needed
                final_reply = full_reply
                if target_lang and target_lang != "en_XX":
                    final_reply = translator.from_english(full_reply, target_lang)

                await websocket.send_json({
                    "type": "done",
                    "reply": final_reply,
                    "detected_language": detected_lang,
                })

            except Exception as e:
                logger.error(f"WebSocket chat error: {e}")
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
