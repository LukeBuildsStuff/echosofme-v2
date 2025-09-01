#!/usr/bin/env python3
"""
Database-connected API for Echoes of Me website
Provides reflections and chat endpoints with PostgreSQL backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
from datetime import datetime
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_CONFIG = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev',
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

app = FastAPI(title="Echoes of Me API", description="Minimal API for website functionality")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ReflectionRequest(BaseModel):
    user_email: str
    question_id: int
    response_text: str
    word_count: Optional[int] = None
    is_draft: Optional[bool] = False

class ChatRequest(BaseModel):
    message: str

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/")
async def root():
    return {
        "message": "Echoes of Me API - Minimal Version", 
        "status": "running",
        "endpoints": ["/reflections", "/chat", "/health"]
    }

@app.post("/reflections")
async def save_reflection(request: ReflectionRequest):
    """Save a user reflection"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # First get user_id from email
        cur.execute("SELECT id FROM users WHERE email = %s", (request.user_email,))
        user_result = cur.fetchone()
        if not user_result:
            raise HTTPException(status_code=404, detail=f"User not found: {request.user_email}")
        
        user_id = user_result[0]
        
        cur.execute("""
            INSERT INTO responses (user_id, question_id, response_text, word_count, is_draft, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, question_id, response_text, word_count, is_draft, created_at, updated_at
        """, (
            user_id,
            request.question_id,
            request.response_text,
            request.word_count or len(request.response_text.split()),
            request.is_draft,
            datetime.now(),
            datetime.now()
        ))
        reflection_row = cur.fetchone()
        reflection = dict(reflection_row)
        reflection['user_email'] = request.user_email  # Add email back for API compatibility
        conn.commit()
        logger.info(f"✅ Saved reflection for user {request.user_email}")
        return reflection
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/reflections/{user_email}")
async def get_reflections(user_email: str):
    """Get reflections for a user"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT r.id, u.email as user_email, r.question_id, r.response_text, r.word_count, r.is_draft, r.created_at, r.updated_at
            FROM responses r
            JOIN users u ON r.user_id = u.id
            WHERE u.email = %s 
            ORDER BY r.created_at DESC
        """, (user_email,))
        reflections = [dict(row) for row in cur.fetchall()]
        logger.info(f"📖 Retrieved {len(reflections)} reflections for user {user_email}")
        return reflections
    except Exception as e:
        logger.error(f"Error retrieving reflections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/reflections/{reflection_id}")
async def delete_reflection(reflection_id: int, user_email: str):
    """Delete a reflection"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM responses 
            WHERE id = %s AND user_id = (SELECT id FROM users WHERE email = %s)
        """, (reflection_id, user_email))
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Reflection not found")
        
        conn.commit()
        logger.info(f"🗑️ Deleted reflection {reflection_id} for user {user_email}")
        return {"message": "Reflection deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/reflections/{reflection_id}")
async def update_reflection(reflection_id: int, request: ReflectionRequest):
    """Update a reflection"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE responses 
            SET response_text = %s, word_count = %s, updated_at = %s
            WHERE id = %s AND user_id = (SELECT id FROM users WHERE email = %s)
            RETURNING id, user_id, question_id, response_text, word_count, is_draft, created_at, updated_at
        """, (
            request.response_text,
            request.word_count or len(request.response_text.split()),
            datetime.now(),
            reflection_id,
            request.user_email
        ))
        
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Reflection not found")
            
        reflection = dict(result)
        reflection['user_email'] = request.user_email  # Add email back for API compatibility
        conn.commit()
        logger.info(f"✏️ Updated reflection {reflection_id} for user {request.user_email}")
        return reflection
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/chat")
async def chat(request: ChatRequest):
    """Simple chat endpoint - returns a helpful message"""
    return {
        "response": "Hello! I'm a temporary Echo while the full system is being restored. Your reflections are being saved, and the full Eleanor experience will be back soon.",
        "status": "ok"
    }

@app.get("/user/{user_email}/answered-questions")
async def get_user_answered_questions(user_email: str):
    """Get all answered question IDs grouped by category for a specific user"""
    import json
    import os
    
    conn = get_db_connection()
    try:
        # Get answered question IDs from database
        cur = conn.cursor()
        cur.execute("""
            SELECT r.question_id
            FROM responses r
            JOIN users u ON r.user_id = u.id
            WHERE u.email = %s
        """, (user_email,))
        
        answered_question_ids = [row[0] for row in cur.fetchall()]
        
        # Load questions.json to get category mappings
        questions_file_path = os.path.join(os.path.dirname(__file__), 'src', 'data', 'questions.json')
        with open(questions_file_path, 'r') as f:
            questions_data = json.load(f)
        
        # Create mapping of question_id to category
        question_id_to_category = {q['id']: q['category'] for q in questions_data}
        
        # Group answered question IDs by category
        answered_by_category = {}
        for question_id in answered_question_ids:
            if question_id in question_id_to_category:
                category = question_id_to_category[question_id]
                if category not in answered_by_category:
                    answered_by_category[category] = []
                answered_by_category[category].append(question_id)
        
        logger.info(f"📊 Retrieved answered questions for {user_email}: {len(answered_by_category)} categories, {len(answered_question_ids)} total questions")
        return answered_by_category
        
    except Exception as e:
        logger.error(f"Error retrieving answered questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/health")
async def health():
    """Health check"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM responses")
        reflections_count = cur.fetchone()[0]
        conn.close()
        logger.info(f"Health check: {reflections_count} reflections in database")
        return {
            "status": "healthy", 
            "database": "connected",
            "reflections_count": reflections_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Echoes of Me API with PostgreSQL...")
    print("📡 API available at: http://localhost:8505")
    print("💾 Using PostgreSQL database for persistence")
    uvicorn.run(app, host="0.0.0.0", port=8505)