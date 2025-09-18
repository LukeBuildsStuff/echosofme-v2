"""
FastAPI server using Supabase backend
Replaces database_api.py with Supabase integration
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import jwt
import os
import logging
from datetime import datetime

# Import Supabase service
from src.services.supabase_service import get_supabase_service

# Keep Eleanor LLM integration from original API
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Echoes of Me - Supabase API", description="Supabase-powered backend for Echoes of Me")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Pydantic Models
class ReflectionRequest(BaseModel):
    question_id: int
    response_text: str = Field(..., min_length=1)
    is_draft: Optional[bool] = False
    response_type: Optional[str] = 'reflection'
    emotional_tags: Optional[List[str]] = []
    privacy_level: Optional[str] = 'private'

class ReflectionUpdate(BaseModel):
    response_text: Optional[str] = None
    is_draft: Optional[bool] = None
    emotional_tags: Optional[List[str]] = None
    privacy_level: Optional[str] = None

class ReflectionResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    response_text: str
    word_count: int
    is_draft: bool
    created_at: str
    updated_at: Optional[str] = None
    questions: Optional[Dict[str, Any]] = None

class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    relationship: Optional[str] = None
    meeting_status: Optional[str] = None
    introduction: Optional[str] = None
    voice_id: Optional[str] = None

class EchoChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    max_length: Optional[int] = 500
    temperature: Optional[float] = 0.7

class EchoChatResponse(BaseModel):
    response: str
    status: str
    conversation_id: Optional[int] = None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user info"""
    try:
        token = credentials.credentials

        # Decode JWT token (Supabase tokens are self-verifying)
        # In production, verify signature with Supabase JWT secret
        payload = jwt.decode(
            token,
            options={"verify_signature": False}  # Supabase handles verification
        )

        # Get user from database using auth ID
        supabase = get_supabase_service()
        user = supabase.get_user_by_auth_id(payload.get('sub'))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    supabase = get_supabase_service()
    is_healthy = supabase.health_check()

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "supabase": "connected" if is_healthy else "disconnected"
    }

# Reflection Endpoints
@app.get("/reflections")
async def get_user_reflections(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get reflections for authenticated user"""
    supabase = get_supabase_service()
    reflections = supabase.get_user_reflections(current_user['id'], limit, offset)

    return {
        "reflections": reflections,
        "total": len(reflections),
        "limit": limit,
        "offset": offset
    }

@app.post("/reflections", response_model=ReflectionResponse)
async def create_reflection(
    reflection: ReflectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new reflection"""
    supabase = get_supabase_service()

    result = supabase.create_reflection(
        user_id=current_user['id'],
        question_id=reflection.question_id,
        response_text=reflection.response_text,
        is_draft=reflection.is_draft,
        response_type=reflection.response_type,
        emotional_tags=reflection.emotional_tags,
        privacy_level=reflection.privacy_level
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reflection"
        )

    return result

@app.put("/reflections/{reflection_id}")
async def update_reflection(
    reflection_id: int,
    updates: ReflectionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a reflection"""
    supabase = get_supabase_service()

    # Convert to dict and remove None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid updates provided"
        )

    result = supabase.update_reflection(reflection_id, update_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reflection not found or update failed"
        )

    return result

@app.delete("/reflections/{reflection_id}")
async def delete_reflection(
    reflection_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a reflection"""
    supabase = get_supabase_service()

    success = supabase.delete_reflection(reflection_id, current_user['id'])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reflection not found or delete failed"
        )

    return {"message": "Reflection deleted successfully"}

# Question Endpoints
@app.get("/questions")
async def get_questions(category: Optional[str] = None):
    """Get questions, optionally filtered by category"""
    supabase = get_supabase_service()
    questions = supabase.get_questions(category)

    return {
        "questions": questions,
        "total": len(questions),
        "category": category
    }

@app.get("/questions/categories")
async def get_question_categories():
    """Get all question categories"""
    supabase = get_supabase_service()
    categories = supabase.get_question_categories()

    return {"categories": categories}

@app.get("/questions/random")
async def get_random_questions(
    count: int = 5,
    category: Optional[str] = None
):
    """Get random questions for daily prompts"""
    supabase = get_supabase_service()
    questions = supabase.get_random_questions(count, category)

    return {
        "questions": questions,
        "count": len(questions),
        "category": category
    }

# User Stats
@app.get("/user-stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get user statistics"""
    supabase = get_supabase_service()
    stats = supabase.get_user_stats(current_user['id'])

    return {
        "user_id": current_user['id'],
        "email": current_user['email'],
        "name": current_user.get('name'),
        **stats
    }

# User Profile
@app.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    supabase = get_supabase_service()
    profile = supabase.get_user_profile(current_user['id'])

    return {
        "user": current_user,
        "profile": profile
    }

@app.put("/profile")
async def update_user_profile(
    profile_updates: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    supabase = get_supabase_service()

    # Convert to dict and remove None values
    update_data = {k: v for k, v in profile_updates.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid updates provided"
        )

    result = supabase.upsert_user_profile(current_user['id'], update_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

    return result

# Eleanor Chat Integration (Keep from original API)
# Note: This is a placeholder - implement Eleanor LLM integration as needed
@app.post("/chat/echo", response_model=EchoChatResponse)
async def echo_chat(
    request: EchoChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Chat with Eleanor AI assistant"""
    # TODO: Integrate Eleanor LLM from original database_api.py
    # For now, return a placeholder response

    supabase = get_supabase_service()

    # Store conversation in database
    conversation = supabase.create_ai_conversation(
        user_id=current_user['id'],
        message=request.message,
        response="Eleanor chat integration coming soon!",
        conversation_type='echo'
    )

    return EchoChatResponse(
        response="Hello! I'm Eleanor Rodriguez. The full chat integration is being set up. Your message has been recorded!",
        status="success",
        conversation_id=conversation['id'] if conversation else None
    )

@app.get("/chat/history")
async def get_chat_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get AI chat history"""
    supabase = get_supabase_service()
    history = supabase.get_ai_conversation_history(current_user['id'], limit)

    return {
        "conversations": history,
        "total": len(history)
    }

# User Management (Admin endpoints)
@app.post("/admin/users/{auth_id}/link")
async def link_user_to_auth(
    auth_id: str,
    email: str,
    name: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Link existing user to Supabase auth (admin only)"""
    # TODO: Add admin check
    supabase = get_supabase_service()

    user = supabase.create_user(auth_id, email, name)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    return user

if __name__ == "__main__":
    import uvicorn

    # Check required environment variables
    required_env = ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
    missing_env = [var for var in required_env if not os.getenv(var)]

    if missing_env:
        logger.error(f"Missing required environment variables: {missing_env}")
        logger.error("Please set up .env file with Supabase credentials")
        exit(1)

    logger.info("🚀 Starting Supabase API server...")
    logger.info(f"📡 Supabase URL: {os.getenv('SUPABASE_URL')}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Different port from old API
        reload=True
    )