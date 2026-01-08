from fastapi import FastAPI, HTTPException, Request, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from backend.nlp.indicbart import IndicBartTranslator
from backend.rag.retriever import VectorStoreRetriever
from backend.rag.generator import generate_answer
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
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ============ Authentication Storage (In-Memory) ============
# Note: This resets on server restart. For production, use a database.
users_db: Dict[str, dict] = {}  # email -> user data
sessions_db: Dict[str, dict] = {}  # session_id -> session data



# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's question or message")
    source_lang: Optional[str] = Field(None, description="Source language code (auto-detect if null)")
    target_lang: Optional[str] = Field(None, description="Preferred response language. If null, defaults to source language.")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Chat history (list of role/content dicts)")
    user_profile: Optional[Dict[str, Any]] = Field(default=None, description="User profile data for personalization")


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
    if session_id and session_id in sessions_db:
        return sessions_db[session_id]
    return None


def create_session(user_id: str, email: str) -> str:
    """Create a new session and return session_id"""
    session_id = str(uuid.uuid4())
    sessions_db[session_id] = {
        "user_id": user_id,
        "email": email,
        "created_at": datetime.now().isoformat()
    }
    return session_id


# ============ Auth Endpoints ============
@app.get("/auth/me")
async def auth_check(request: Request):
    """Check current authentication status"""
    session = get_session_from_cookie(request)
    
    # Generate a session_id for tracking even if not logged in
    anonymous_session_id = str(uuid.uuid4())
    
    if session:
        user = users_db.get(session["email"])
        if user:
            return {
                "is_logged_in": True,
                "user_id": user["user_id"],
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
    user = users_db.get(email)
    if not user:
        return {"success": False, "message": "No account found with this email. Please sign up first."}
    
    # Check password (simple comparison - production should use bcrypt)
    if user["password"] != req.password:
        return {"success": False, "message": "Incorrect password. Please try again."}
    
    # Create session
    session_id = create_session(user["user_id"], email)
    
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
            "user_id": user["user_id"],
            "name": user["name"]
        }
    }


@app.post("/auth/logout")
async def auth_logout(request: Request, response: Response):
    """Log out and clear session"""
    session_id = request.cookies.get("session_id")
    
    # Remove session from storage
    if session_id and session_id in sessions_db:
        del sessions_db[session_id]
    
    # Clear the cookie
    response.delete_cookie(key="session_id")
    
    logger.info("User logged out")
    return {"success": True}


@app.post("/profile")
async def create_profile(req: ProfileRequest, response: Response):
    """Create a new user profile (sign up)"""
    email = req.email.lower().strip()
    
    # Check if user already exists
    if email in users_db:
        return {"success": False, "message": "An account with this email already exists. Please sign in."}
    
    # Create user
    user_id = str(uuid.uuid4())
    users_db[email] = {
        "user_id": user_id,
        "email": email,
        "password": req.password,  # Production: hash this
        "name": req.name,
        "gender": req.gender,
        "age": req.age,
        "state": req.state,
        "area": req.area,
        "category": req.category,
        "is_disabled": req.is_disabled,
        "is_minority": req.is_minority,
        "is_student": req.is_student,
        "employment_status": req.employment_status,
        "is_govt_employee": req.is_govt_employee,
        "annual_income": req.annual_income,
        "family_income": req.family_income,
        "created_at": datetime.now().isoformat()
    }
    
    # Auto-login: create session
    session_id = create_session(user_id, email)
    
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
    
    user = users_db.get(session["email"])
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
    
    user = users_db.get(session["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            user[key] = value
    
    users_db[session["email"]] = user
    
    logger.info(f"Profile updated: {session['email']}")
    
    return {"success": True, "message": "Profile updated successfully"}


# API Endpoints

@app.get("/")
async def serve_frontend():
    """Serve the frontend index.html"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


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
        
        # Step 1: Detect or validate source language
        if req.source_lang is None:
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
        
        # Step 3: Retrieve relevant documents
        docs = retriever.search(english_message, k=4)
        

        
        # Step 4: Generate answer
        context = "\n\n".join([doc.page_content for doc in docs])
        reply = generate_answer(
            user_question=english_message,
            context=context,
            history=req.history,
            user_profile=req.user_profile
        )
        
        # Step 5: Translate response if needed
        if target_lang != "en_XX":
            reply = translator.from_english(reply, target_lang)
            logger.info(f"Translated response to {target_lang}")
        
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