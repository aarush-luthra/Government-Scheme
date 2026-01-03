from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from backend.nlp.indicbart import IndicBartTranslator
from backend.rag.retriever import VectorStoreRetriever
from backend.rag.generator import generate_answer
from backend.database import (
    save_message, get_session_messages, count_bot_responses,
    get_message_summary, get_session, save_user_profile
)
from backend.auth import (
    register_user, login_user, create_user_session,
    link_session_to_user, validate_session, logout
)
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
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Cookie, Response
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



# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's question or message")
    source_lang: Optional[str] = Field(None, description="Source language code (auto-detect if null)")
    target_lang: Optional[str] = Field(None, description="Preferred response language. If null, defaults to source language.")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Chat history (list of role/content dicts)")


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


# Auth Request/Response Models
class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=2, description="User's full name")
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict] = None


class SessionInfo(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    is_logged_in: bool


class ProfileRequest(BaseModel):
    """Scheme Finder form data"""
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    state: Optional[str] = None
    area: Optional[str] = None
    category: Optional[str] = None
    is_disabled: Optional[bool] = False
    is_minority: Optional[bool] = False
    is_student: Optional[bool] = False
    employment_status: Optional[str] = None
    is_govt_employee: Optional[bool] = False
    annual_income: Optional[float] = None
    family_income: Optional[float] = None


# Max bot responses before auth wall for anonymous users
MAX_ANONYMOUS_RESPONSES = 3


@app.get("/")
async def serve_frontend():
    """Serve the frontend index.html"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Government Scheme Assistant",
        "supported_languages": len(translator.get_supported_languages())
    }


# ============ Authentication Endpoints ============

@app.post("/auth/signup", response_model=AuthResponse)
async def signup(req: SignUpRequest, response: Response, session_id: Optional[str] = Cookie(None)):
    """
    Register a new user.
    If session_id cookie exists, links the anonymous session to the new user.
    """
    try:
        success, message, user_id = register_user(req.name, req.email, req.password)
        
        if not success:
            return AuthResponse(success=False, message=message)
        
        # Create new session for user or link existing anonymous session
        if session_id:
            # Link existing session to new user
            link_session_to_user(session_id, user_id)
            new_session_id = session_id
        else:
            # Create new session
            new_session_id = create_user_session(user_id)
        
        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            httponly=True,
            max_age=60 * 60 * 24 * 30,  # 30 days
            samesite="lax"
        )
        
        return AuthResponse(
            success=True,
            message="Registration successful",
            user={
                "user_id": user_id,
                "name": req.name,
                "email": req.email
            }
        )
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/auth/login", response_model=AuthResponse)
async def login(req: LoginRequest, response: Response, session_id: Optional[str] = Cookie(None)):
    """
    Authenticate a user.
    If session_id cookie exists (anonymous session), links it to the logged-in user.
    """
    try:
        success, message, user_data = login_user(req.email, req.password)
        
        if not success:
            return AuthResponse(success=False, message=message)
        
        # Link existing session or create new one
        if session_id:
            link_session_to_user(session_id, user_data['user_id'])
            new_session_id = session_id
        else:
            new_session_id = create_user_session(user_data['user_id'])
        
        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            httponly=True,
            max_age=60 * 60 * 24 * 30,  # 30 days
            samesite="lax"
        )
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user=user_data
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.post("/auth/logout")
async def logout_user(response: Response, session_id: Optional[str] = Cookie(None)):
    """Log out the current user by deleting their session."""
    if session_id:
        logout(session_id)
    
    response.delete_cookie("session_id")
    return {"success": True, "message": "Logged out successfully"}


@app.get("/auth/me", response_model=SessionInfo)
async def get_current_user(response: Response, session_id: Optional[str] = Cookie(None)):
    """Get current user session info."""
    if not session_id:
        # Create anonymous session
        new_session_id = create_user_session()
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            httponly=True,
            max_age=60 * 60 * 24 * 30,
            samesite="lax"
        )
        return SessionInfo(
            session_id=new_session_id,
            is_logged_in=False
        )
    
    # Validate existing session
    session_info = validate_session(session_id)
    
    if not session_info:
        # Session doesn't exist, create new anonymous session
        new_session_id = create_user_session()
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            httponly=True,
            max_age=60 * 60 * 24 * 30,
            samesite="lax"
        )
        return SessionInfo(
            session_id=new_session_id,
            is_logged_in=False
        )
    
    return SessionInfo(**session_info)


@app.post("/profile")
async def save_profile(
    req: ProfileRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None)
):
    """
    Save or Update user profile.
    """
    from backend.auth import hash_password
    from backend.database import get_user_profile, save_user_profile, update_user_profile 
    
    try:
        # Ensure we have a session
        if not session_id:
            session_id = create_user_session()
            response.set_cookie(
                key="session_id", value=session_id, httponly=True, max_age=60*60*24*30, samesite="lax"
            )
        
        # Build profile data
        profile_data = {
            'name': req.name,
            'email': req.email,
            'gender': req.gender,
            'age': req.age,
            'state': req.state,
            'area': req.area,
            'category': req.category,
            'is_disabled': req.is_disabled,
            'is_minority': req.is_minority,
            'is_student': req.is_student,
            'employment_status': req.employment_status,
            'is_govt_employee': req.is_govt_employee,
            'annual_income': req.annual_income,
            'family_income': req.family_income
        }

        # Handle Password (only hash if provided)
        if req.password:
            profile_data['password_hash'] = hash_password(req.password)
        else:
            profile_data['password_hash'] = None

        # CHECK: Does profile exist?
        existing_profile = get_user_profile(session_id)
        
        # Get user_id from session if logged in
        session = get_session(session_id)
        user_id = session.get('user_id') if session else None

        if existing_profile:
            # UPDATE
            success = update_user_profile(session_id, profile_data)
            profile_id = existing_profile.get('id') # Keep existing ID
            msg = "Profile updated successfully"
        else:
            # INSERT - pass user_id to save function
            profile_id = save_user_profile(session_id, profile_data, user_id)
            msg = "Profile saved successfully"
            
            # If email provided on creation, try to register/link user
            if req.email and req.password and req.name and not user_id:
                success_reg, _, new_user_id = register_user(req.name, req.email, req.password)
                if success_reg and new_user_id:
                    link_session_to_user(session_id, new_user_id)
                    user_id = new_user_id
                    print("\n\n" + "="*50)

            print(f"NEW USER PROFILE SAVED (ID: {profile_id})")

            print("="*50)

            for key, value in profile_data.items():

                if key != 'password_hash':  # Don't print sensitive data

                    print(f"{key.ljust(20)}: {value}")

            print("="*50 + "\n\n")

        return {
            "success": True,
            "profile_id": profile_id,
            "message": msg
        }
        
    except Exception as e:
        logger.error(f"Profile save error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save profile")


@app.get("/profile")
async def get_profile(session_id: Optional[str] = Cookie(None)):
    """
    Get the latest profile for the current session.
    """
    from backend.database import get_user_profile, get_user_profile_by_user_id, get_session
    
    if not session_id:
        return {}
    
    # Check if user is logged in (session has user_id)
    session = get_session(session_id)
    if session and session.get('user_id'):
        # Fetch by user_id (persists across sessions)
        profile = get_user_profile_by_user_id(session['user_id'])
    else:
        # Fallback to session_id (for anonymous users)
        profile = get_user_profile(session_id)
    
    if not profile:
        return {}
        
    # Remove sensitive data
    if 'password_hash' in profile:
        del profile['password_hash']
        
    return profile


@app.get("/edit")
async def get_edit_profile(session_id: Optional[str] = Cookie(None)):
    """
    Get profile data specifically for the edit page. 
    This is an alias for /profile but distinct for logging.
    """
    return await get_profile(session_id)


@app.post("/edit")
async def edit_profile(
    req: ProfileRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None)
):
    """
    Update user profile from Edit Profile form.
    """
    from backend.auth import hash_password
    from backend.database import get_user_profile, save_user_profile, update_user_profile 
    
    try:
        if not session_id:
            raise HTTPException(status_code=401, detail="Session required")

        # Build profile data
        profile_data = {
            'name': req.name,
            'email': req.email,
            'gender': req.gender,
            'age': req.age,
            'state': req.state,
            'area': req.area,
            'category': req.category,
            'is_disabled': req.is_disabled,
            'is_minority': req.is_minority,
            'is_student': req.is_student,
            'employment_status': req.employment_status,
            'is_govt_employee': req.is_govt_employee,
            'annual_income': req.annual_income,
            'family_income': req.family_income
        }

        # Handle Password (only hash if provided)
        if req.password:
            profile_data['password_hash'] = hash_password(req.password)
        else:
            profile_data['password_hash'] = None

        # Always Update in Edit Mode
        success = update_user_profile(session_id, profile_data)
        
        # Log to terminal
        print(f"\n[EDIT PROFILE] Profile updated for session: {session_id}")

        return {
            "success": True,
            "message": "Profile updated successfully (via /edit)"
        }
        
    except Exception as e:
        logger.error(f"Edit profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


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
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Translation failed")


@app.post("/translate/batch")
async def batch_translate(req: BatchTranslateRequest):
    try:
        # 1. Validation
        if req.target_lang not in translator.SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=400, detail=f"Unsupported target language: {req.target_lang}")

        # 2. Call the optimized batch function
        # Note: We do NOT force source_lang to 'en_XX' here. 
        # We pass None if it's missing, letting the Translator class detect it.
        translations = translator.batch_translate(
            req.texts,
            source_lang=req.source_lang, 
            target_lang=req.target_lang
        )
        
        return {
            "translations": translations,
            "source_lang": req.source_lang or "auto",
            "target_lang": req.target_lang
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Translation failed")


@app.post("/chat")
async def chat(
    req: ChatRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None)
):
    """
    Chat with the assistant about government schemes.
    Supports all Indic languages with automatic translation.
    
    - **message**: User's question (in any supported language)
    - **source_lang**: Language of the message (auto-detect if null)
    - **target_lang**: Preferred language for response (default: source language)
    - **history**: List of previous messages for context
    
    Returns auth_required=true if anonymous user exceeds response limit.
    """
    try:
        # Ensure we have a session
        if not session_id:
            session_id = create_user_session()
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                max_age=60 * 60 * 24 * 30,
                samesite="lax"
            )
        else:
            # Validate session exists
            session = get_session(session_id)
            if not session:
                session_id = create_user_session()
                response.set_cookie(
                    key="session_id",
                    value=session_id,
                    httponly=True,
                    max_age=60 * 60 * 24 * 30,
                    samesite="lax"
                )
        
        # Get session info for context injection
        session_info = validate_session(session_id)
        is_logged_in = session_info and session_info.get('is_logged_in', False)
        
        # Check auth wall for anonymous users
        if not is_logged_in:
            bot_response_count = count_bot_responses(session_id)
            if bot_response_count >= MAX_ANONYMOUS_RESPONSES:
                return JSONResponse(content={
                    "reply": None,
                    "auth_required": True,
                    "message": "Sign in or create an account to continue chatting",
                    "response_count": bot_response_count
                })
        
        # Save user message to database
        save_message(session_id, "user", req.message)
        
        original_message = req.message
        detected_lang = None
        language_name = None
        
        # Step 1: Detect or validate source language
        if req.source_lang is None:
            detected_lang = translator.detect_language_code(req.message)
            if detected_lang is None:
                detected_lang = "en_XX"
            source_lang = detected_lang
        else:
            source_lang = req.source_lang
            detected_lang = source_lang
        
        # Step 1.5: Determine target language
        target_lang = req.target_lang if req.target_lang else source_lang
        
        language_name = translator.SUPPORTED_LANGUAGES.get(detected_lang, "Unknown")
        logger.info(f"Processing message in {language_name} ({detected_lang}) -> Respond in {target_lang}")
        
        # Step 2: Translate to English if needed
        if source_lang != "en_XX":
            english_message = translator.to_english(req.message, source_lang=source_lang)
            logger.info(f"Translated query: {english_message}")
        else:
            english_message = req.message
        
        # Step 3: Retrieve relevant documents
        docs = retriever.search(english_message, k=4)
        
        # Step 4: Build context with user info if logged in
        doc_context = "\n\n".join([doc.page_content for doc in docs])
        
        # Context injection
        system_context = ""
        if is_logged_in and session_info:
            user_name = session_info.get('user_name', 'User')
            user_id = session_info.get('user_id')
            message_summary = get_message_summary(session_id, limit=5)
            system_context = f"""
User Information:
- Name: {user_name}
- User ID: {user_id}

Previous Conversation Summary:
{message_summary}
"""
        else:
            system_context = f"""
Anonymous Session ID: {session_id}
"""
        
        # Combine contexts
        full_context = f"{system_context}\n\nRelevant Information:\n{doc_context}"
        
        # Step 5: Generate answer
        reply = generate_answer(
            user_question=english_message,
            context=full_context,
            history=req.history
        )
        
        # Step 6: Translate response if needed
        if target_lang != "en_XX":
            reply = translator.from_english(reply, target_lang)
            logger.info(f"Translated response to {target_lang}")
        
        # Save bot response to database
        save_message(session_id, "bot", reply)
        
        # Get updated response count for anonymous users
        response_count = count_bot_responses(session_id) if not is_logged_in else None
        
        return JSONResponse(content={
            "reply": reply,
            "detected_language": detected_lang,
            "language_name": language_name,
            "original_message": original_message,
            "translated_message": english_message if source_lang != "en_XX" else None,
            "auth_required": False,
            "response_count": response_count,
            "remaining_free": MAX_ANONYMOUS_RESPONSES - response_count if response_count else None
        })
        
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
    uvicorn.run(app, host="127.0.0.1", port=8000)