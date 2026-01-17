from fastapi import FastAPI, HTTPException, Request, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from backend.nlp.indicbart import IndicBartTranslator
from backend.rag.retriever import VectorStoreRetriever
from backend.rag.generator import generate_answer
from backend import database as db  # Import database module
from backend.routes.ocr_routes import router as ocr_router  # OCR functionality
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Government Scheme Assistant",
    description="Multi-language AI assistant for Indian government schemes",
    version="2.0.0"
)

# Initialize translator (single instance for efficiency)
translator = IndicBartTranslator()

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize retriever
retriever = VectorStoreRetriever()

# Determine frontend path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount frontend static files
# Mount frontend static files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Include OCR router
app.include_router(ocr_router, prefix="/api/v1", tags=["OCR"])

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204) # No content, stops 404 logs

# ============ Authentication Storage (SQLite) ============
# User data and sessions are now stored in SQLite database via database.py



# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's question or message")
    source_lang: Optional[str] = Field(None, description="Source language code (auto-detect if null)")
    target_lang: Optional[str] = Field(None, description="Preferred response language. If null, defaults to source language.")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Chat history (list of role/content dicts)")
    user_profile: Optional[Dict[str, Any]] = Field(default=None, description="User profile data for personalization")
    user_id: Optional[str] = Field(default=None, description="User ID for loading profile and persisting chat history")


class ChatResponse(BaseModel):
    reply: str
    detected_language: Optional[str] = None
    language_name: Optional[str] = None
    original_message: Optional[str] = None
    translated_message: Optional[str] = None



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
    session = get_session_from_cookie(request)
    
    # Generate a session_id for tracking even if not logged in
    anonymous_session_id = str(uuid.uuid4())
    
    if session:
        user = db.get_user_by_email(session["email"])
        if user:
            return {
                "is_logged_in": True,
                "user_id": user["id"],
                "user_name": user["name"],
                "session_id": request.cookies.get("session_id")
            }
    
    return {
        "is_logged_in": False,
        "session_id": anonymous_session_id
    }


@app.post("/auth/login")
async def auth_login(req: LoginRequest, response: Response):
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
    
    logger.info(f"User logged in: {email}")
    
    return {
        "success": True,
        "user": {
            "user_id": user["id"],
            "name": user["name"]
        }
    }


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
async def create_profile(req: ProfileRequest, response: Response):
    """Create a new user profile (sign up)"""
    email = req.email.lower().strip()
    
    # Create user in database
    result = db.create_user(
        email=email,
        password=req.password,
        name=req.name,
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
        family_income=req.family_income
    )
    
    if not result:
        return {"success": False, "message": "An account with this email already exists. Please sign in."}
    
    user_id = result["user_id"]
    
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
        "user_id": user_id
    }


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
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user["name"],
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
        "family_income": user.get("family_income")
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
    success = db.update_user(session["email"], **update_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    
    logger.info(f"Profile updated: {session['email']}")
    
    return {"success": True, "message": "Profile updated successfully"}


# API Endpoints

@app.get("/")
async def serve_frontend():
    """Serve the frontend index.html"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/auth/login")
async def serve_login_page():
    """Serve the login page"""
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/signup")
async def serve_signup_page():
    """Serve the signup page"""
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))


@app.get("/profile")
async def serve_profile_page():
    """Serve the signup/profile page (alias for signup)"""
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))


@app.get("/onboarding")
async def serve_onboarding():
    """Serve the onboarding page for new users"""
    return FileResponse(os.path.join(FRONTEND_DIR, "onboarding.html"))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Government Scheme Assistant",
        "supported_languages": len(translator.get_supported_languages())
    }


@app.get("/languages", response_model=List[LanguageInfo])
async def get_supported_languages():
    """Get list of all supported languages"""
    languages = translator.get_supported_languages()
    return [
        LanguageInfo(code=code, name=name) 
        for code, name in languages.items()
    ]


@app.post("/translate", response_model=TranslateResponse)
async def translate_text(req: TranslateRequest):
    """
    Translate text between any supported languages
    
    - **text**: Text to translate
    - **source_lang**: Source language code (optional, will auto-detect)
    - **target_lang**: Target language code (default: English)
    """
    try:
        # Auto-detect if source_lang not provided
        if req.source_lang is None:
            detected_lang = translator.detect_language_code(req.text)
            if detected_lang is None:
                raise HTTPException(
                    status_code=400, 
                    detail="Could not detect source language. Please specify source_lang."
                )
            source_lang = detected_lang
        else:
            source_lang = req.source_lang
        
        # Validate language codes
        supported = translator.get_supported_languages()
        if source_lang not in supported:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported source language: {source_lang}"
            )
        if req.target_lang not in supported:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported target language: {req.target_lang}"
            )
        
        # Perform translation
        translation = translator.translate(
            req.text,
            source_lang=source_lang,
            target_lang=req.target_lang
        )
        
        return TranslateResponse(
            translation=translation,
            source_lang=source_lang,
            target_lang=req.target_lang
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail="Translation failed")


@app.post("/translate/batch")
async def batch_translate(req: BatchTranslateRequest):
    """
    Translate multiple texts at once
    
    - **texts**: List of texts to translate
    - **source_lang**: Source language code (optional)
    - **target_lang**: Target language code
    """
    try:
        translations = translator.batch_translate(
            req.texts,
            source_lang=req.source_lang,
            target_lang=req.target_lang
        )
        
        return {
            "translations": translations,
            "count": len(translations),
            "source_lang": req.source_lang,
            "target_lang": req.target_lang
        }
        
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail="Batch translation failed")


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Chat with the assistant about government schemes
    Supports all Indic languages with automatic translation
    
    - **message**: User's question (in any supported language)
    - **source_lang**: Language of the message (auto-detect if null)
    - **target_lang**: Preferred language for response (default: source language)
    - **history**: List of previous messages for context
    """
    try:
        original_message = req.message
        detected_lang = None
        language_name = None
        
        # Load user profile from database if user_id provided and no profile in request
        user_profile = req.user_profile
        if req.user_id and not user_profile:
            user_profile = db.get_user_profile_for_chat(req.user_id)
            if user_profile:
                logger.info(f"Loaded profile from database for user: {req.user_id}")
        
        # Load chat history from database if user_id provided
        db_chat_history = []
        if req.user_id:
            db_chat_history = db.get_chat_history(req.user_id)
            if db_chat_history:
                logger.info(f"Loaded {len(db_chat_history)} chat entries from database")
        
        # Step 1: Detect or validate source language
        if req.source_lang is None or req.source_lang == "auto":
            detected_lang = translator.detect_language_code(req.message)
            if detected_lang is None:
                # Assume English if detection fails
                detected_lang = "en_XX"
            source_lang = detected_lang
        else:
            source_lang = req.source_lang
            detected_lang = source_lang
        
        # Step 1.5: Determine target language (default to source if not provided)
        target_lang = req.target_lang if req.target_lang else source_lang
        
        language_name = translator.SUPPORTED_LANGUAGES.get(detected_lang, "Unknown")
        logger.info(f"Processing message in {language_name} ({detected_lang}) -> Respond in {target_lang}")
        
        # Step 2: Translate to English if needed (for RAG retrieval)
        if source_lang != "en_XX":
            english_message = translator.to_english(req.message, source_lang=source_lang)
            logger.info(f"Translated query: {english_message}")
        else:
            english_message = req.message
        
        # Step 3: Retrieve relevant documents using profile-aware search
        if user_profile:
            # Use profile-based multi-query search for better eligibility matching
            docs = retriever.search_by_profile(user_profile, k=8)
            logger.info(f"Profile-based search returned {len(docs)} documents")
        else:
            # Standard query search
            docs = retriever.search(english_message, k=6)
        
        # Merge database chat history with request history
        merged_history = req.history or []
        if db_chat_history:
            # Convert database format to chat format (last 10 entries)
            for entry in db_chat_history[-10:]:
                merged_history.append({"role": "user", "content": entry["question"]})
                merged_history.append({"role": "assistant", "content": entry["answer"]})
        
        # Step 4: Generate answer with strict eligibility checking
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])
        reply = generate_answer(
            user_question=english_message,
            context=context,
            history=merged_history,
            user_profile=user_profile
        )
        
        # Step 5: Translate response if needed
        if target_lang != "en_XX":
            reply = translator.from_english(reply, target_lang)
            logger.info(f"Translated response to {target_lang}")
        
        # Extract source titles
        source_titles = sorted(list(set([
            doc.metadata.get("scheme_name") or doc.metadata.get("title", "Unknown Scheme")
            for doc in docs
        ])))
        
        # Save chat entry to database for authenticated users
        if req.user_id:
            db.append_chat_entry(req.user_id, original_message, reply)
            logger.info(f"Saved chat entry for user: {req.user_id}")

        return ChatResponse(
            reply=reply,
            detected_language=detected_lang,
            language_name=language_name,
            original_message=original_message,
            translated_message=english_message if source_lang != "en_XX" else None
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
    """
    Simplified multilingual chat endpoint
    
    - Automatically detects language
    - Responds in the same language as the question
    """
    try:
        # Detect source language
        source_lang = translator.detect_language_code(message) if auto_detect else "en_XX"
        
        # Determine target language
        target_lang = source_lang if respond_in_same_language else "en_XX"
        
        # Use main chat endpoint logic
        req = ChatRequest(
            message=message,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        return await chat(req)
        
    except Exception as e:
        logger.error(f"Multilingual chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check for translator
@app.get("/health/translator")
async def translator_health():
    """Check if translator is working"""
    try:
        # Test translation
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)