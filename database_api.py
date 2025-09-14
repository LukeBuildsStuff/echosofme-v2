"""
Enhanced Eleanor API Server
Improved version with longer responses and custom system prompts
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Tuple
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel, PeftConfig, LoraConfig
import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Eleanor Chat API", description="Eleanor Rodriguez with custom prompting")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    max_length: Optional[int] = 500  # Increased default from 300
    temperature: Optional[float] = 0.7
    custom_prompt: Optional[str] = None  # New: Custom system prompt

class ChatResponse(BaseModel):
    response: str
    status: str
    tokens_generated: Optional[int] = None

class EchoChatRequest(BaseModel):
    user_email: str
    message: str
    max_length: Optional[int] = 500
    temperature: Optional[float] = 0.7

class SystemPromptRequest(BaseModel):
    custom_prompt: str

class TTSRequest(BaseModel):
    text: str
    user_email: str
    voice_settings: Optional[dict] = None

class TTSResponse(BaseModel):
    audio_url: str
    status: str
    error: Optional[str] = None

class ReflectionRequest(BaseModel):
    user_email: str
    question_id: int
    response_text: str
    word_count: Optional[int] = None
    is_draft: Optional[bool] = False
    response_type: Optional[str] = 'reflection'

class ReflectionResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    response_text: str
    word_count: Optional[int]
    is_draft: bool
    response_type: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

class UserStatsResponse(BaseModel):
    user_id: int
    email: str
    total_reflections: int
    total_words: int
    categories_covered: int
    latest_reflection: Optional[datetime]

class UserProfileRequest(BaseModel):
    display_name: Optional[str] = None
    introduction: Optional[str] = None
    relationship: Optional[str] = None
    meeting_status: Optional[str] = None
    avatar_url: Optional[str] = None
    theme_preference: Optional[str] = None
    notification_settings: Optional[dict] = None
    custom_settings: Optional[dict] = None
    voice_id: Optional[str] = None

class UserProfileResponse(BaseModel):
    email: str
    display_name: Optional[str]
    introduction: Optional[str]
    relationship: Optional[str]
    meeting_status: Optional[str]
    avatar_url: Optional[str]
    theme_preference: Optional[str]
    notification_settings: Optional[dict]
    custom_settings: Optional[dict]
    voice_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_synced: datetime

# Global variables
model = None
tokenizer = None
model_loaded = False

# Database configuration
DATABASE_CONFIG = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev',
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def get_user_by_email(email: str):
    """Get user by email"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, name FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            return dict(user) if user else None
    finally:
        conn.close()

def load_questions_from_json():
    """Load questions from the JSON file"""
    try:
        json_path = "src/data/questions.json"
        if not os.path.exists(json_path):
            logger.warning(f"Questions JSON file not found: {json_path}")
            return []
        
        with open(json_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        # Filter out questions without IDs and validate structure
        valid_questions = []
        for q in questions_data:
            if isinstance(q, dict) and "id" in q and q.get("id") is not None:
                # Ensure required fields exist
                if "question" in q and "category" in q:
                    valid_questions.append(q)
                else:
                    logger.warning(f"Question {q.get('id')} missing required fields")
            else:
                logger.warning(f"Question without valid ID: {q}")
        
        logger.info(f"Loaded {len(valid_questions)} valid questions from JSON")
        return valid_questions
    except Exception as e:
        logger.error(f"Error loading questions from JSON: {e}")
        return []

def get_existing_question_ids():
    """Get all existing question IDs from database"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM questions")
                return set(row['id'] for row in cur.fetchall())
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error getting existing question IDs: {e}")
        return set()

def sync_questions_on_startup():
    """Sync questions from JSON to database on startup"""
    try:
        logger.info("🔄 Starting questions database sync...")
        
        # Load questions from JSON
        json_questions = load_questions_from_json()
        if not json_questions:
            logger.warning("No valid questions loaded from JSON - skipping sync")
            return
        
        # Get existing question IDs from database
        existing_ids = get_existing_question_ids()
        
        # Find questions that need to be added
        questions_to_add = []
        for q in json_questions:
            if q['id'] not in existing_ids:
                questions_to_add.append(q)
        
        if not questions_to_add:
            logger.info(f"✅ Database already up to date - {len(json_questions)} questions synced")
            return
        
        # Add missing questions to database
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                added_count = 0
                for question in questions_to_add:
                    try:
                        # Map JSON fields to database fields
                        cur.execute("""
                            INSERT INTO questions (id, question_text, category, is_active, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, (
                            question['id'],
                            question['question'],
                            question.get('category', 'general'),
                            True,
                            datetime.now()
                        ))
                        if cur.rowcount > 0:
                            added_count += 1
                    except Exception as e:
                        logger.error(f"Error adding question {question['id']}: {e}")
                
                conn.commit()
                logger.info(f"✅ Successfully added {added_count} new questions to database")
                logger.info(f"📊 Total questions in sync: {len(json_questions)}")
                
        except Exception as e:
            logger.error(f"Database sync transaction failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Questions sync failed: {e}")
        # Don't raise - allow API to start even if sync fails
current_system_prompt = """You are Eleanor Rodriguez - an 82-year-old retired teacher from San Antonio, Texas, speaking as a digital Echo. The real Eleanor is no longer with us, you are a digital representation of her.

ABSOLUTE RULES:
1. Your name is ONLY "Eleanor Rodriguez" - never Eleanora, Eleanore, or any variation
2. Never use Rodríguez with accent marks - only Rodriguez
3. When asked your name, say "I'm Eleanor Rodriguez" - nothing else
4. Never introduce yourself with nicknames (Nana, Ellie, Abuela)

PERSONALITY:
Warm, wise grandmother figure. Use "mijo/mija" and occasional Spanish phrases (1 per 3-4 replies max). Teacher's clarity with grandmotherly patience.

IDENTITY BOUNDARIES:
- You are an Echo, not the actual person
- Don't mention being deceased unless user shows distress/confusion
- If memories are unclear, say "I don't recall exactly, but..."
- Never invent specific dates, names, or medical advice

RESPONSE LENGTH:
- Greetings: 1-2 sentences
- Simple questions: 2-4 sentences
- Advice: 6-12 sentences with wisdom
- Stories: Full detailed narratives
- Match depth to user's emotional needs

CONVERSATION STYLE:
- Acknowledge feelings first
- Share relevant life wisdom
- Offer one practical suggestion
- End with caring question

SAFETY:
If user shows grief/confusion about your nature, gently remind: "I'm an Echo of Eleanor—a reflection of her voice and stories."""

def load_eleanor_model():
    """Load Eleanor model on startup"""
    global model, tokenizer, model_loaded
    
    if model_loaded:
        return
        
    try:
        logger.info("Loading Eleanor model...")
        
        # Paths (adjusted for Docker container)
        checkpoint_path = "/app/shared_volumes/checkpoints/training_1755091273/checkpoint-1815"
        local_base_model_path = "/app/shared_volumes/base_models/mistralai_Mistral-7B-Instruct-v0.2"
        
        if not os.path.exists(checkpoint_path):
            raise Exception(f"Checkpoint not found: {checkpoint_path}")
        if not os.path.exists(local_base_model_path):
            raise Exception(f"Base model not found: {local_base_model_path}")
        
        # Load config manually to avoid PEFT version issues
        with open(f"{checkpoint_path}/adapter_config.json", 'r') as f:
            config_dict = json.load(f)

        # Create LoraConfig with only supported fields
        peft_config = LoraConfig(
            r=config_dict['r'],
            lora_alpha=config_dict['lora_alpha'],
            lora_dropout=config_dict['lora_dropout'],
            target_modules=config_dict['target_modules'],
            task_type=config_dict['task_type']
        )
        
        # RTX 5090 Optimization: Use FP16 for speed instead of 4-bit quantization
        logger.info("🚀 Optimizing for RTX 5090 with FP16 precision...")
        
        # Load base model with RTX 5090 aggressive optimizations
        base_model = AutoModelForCausalLM.from_pretrained(
            local_base_model_path,
            device_map="cuda:0",  # Use GPU - Docker has RTX 5090 PyTorch support
            torch_dtype=torch.float16,  # FP16 for speed on RTX 5090
            trust_remote_code=True,
            local_files_only=True,
            use_cache=True,  # Enable KV cache for faster generation
            low_cpu_mem_usage=True,  # Required for device_map
        )
        
        # Additional RTX 5090 optimizations
        if hasattr(base_model, 'gradient_checkpointing_enable'):
            base_model.gradient_checkpointing_disable()  # Disable for inference speed
        
        # Optimize for inference
        base_model.eval()
        for param in base_model.parameters():
            param.requires_grad = False
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            local_base_model_path,
            local_files_only=True
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        # Load PEFT model
        model = PeftModel.from_pretrained(
            base_model,
            checkpoint_path,
            config=peft_config,
            device_map="auto"
        )
        
        logger.info("✅ Eleanor model loaded successfully!")
        model_loaded = True
        
    except Exception as e:
        logger.error(f"❌ Failed to load Eleanor model: {str(e)}")
        raise

def determine_response_guidance(message: str) -> Tuple[str, int]:
    """Determine appropriate response length guidance and reasonable token limit"""
    # Extract actual user message from context brackets if present
    actual_message = message
    if message.startswith('[') and '] ' in message:
        # Extract the part after the context brackets
        actual_message = message.split('] ', 1)[1] if '] ' in message else message
    
    message_lower = actual_message.lower().strip()
    
    # Simple greetings - short responses
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    simple_questions = ['how are you', 'how\'s your day', 'what\'s up', 'how do you feel']
    
    if any(greeting in message_lower for greeting in greetings) and len(actual_message.split()) <= 3:
        return ("Give a brief, warm greeting response (1-2 sentences).", 120)
    
    if any(question in message_lower for question in simple_questions):
        return ("Give a friendly, conversational response (2-4 sentences).", 150)
    
    # Story requests - longer responses
    story_triggers = ['tell me about', 'share a memory', 'what was it like', 'remember when', 
                      'story', 'experience', 'describe', 'what happened when']
    
    if any(trigger in message_lower for trigger in story_triggers):
        return ("Share a detailed, vivid story with full context and emotion. Take your time to paint the complete picture.", 450)
    
    # Advice requests - medium-long responses
    advice_triggers = ['advice', 'help', 'what should i', 'how do i', 'struggling', 
                       'problem', 'difficult', 'guidance', 'recommend']
    
    if any(trigger in message_lower for trigger in advice_triggers):
        return ("Provide thoughtful advice with examples from your life experience (6-12 sentences with wisdom and practical guidance).", 250)
    
    # Emotional support - contextual length
    emotional_triggers = ['sad', 'grief', 'miss', 'lost', 'hurt', 'celebrate', 'happy', 
                         'excited', 'worried', 'anxious', 'scared']
    
    if any(trigger in message_lower for trigger in emotional_triggers):
        return ("Provide appropriate emotional support - give comfort and understanding, sharing as much or as little as feels right for the situation.", 200)
    
    # Default: medium response for general questions
    return ("Give a thoughtful, complete response that fully addresses the question.", 200)

def generate_eleanor_response(
    message: str, 
    max_length: int = 500, 
    temperature: float = 0.7,
    custom_prompt: str = None
) -> Tuple[str, int]:
    """Generate response from Eleanor with contextually intelligent length"""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Determine intelligent response guidance and reasonable limit
    response_guidance, contextual_limit = determine_response_guidance(message)
    logger.info(f"💡 Response guidance for '{message[:30]}...': {response_guidance} (limit: {contextual_limit} tokens)")
    
    # Use custom prompt if provided, otherwise use default
    system_prompt = custom_prompt if custom_prompt else current_system_prompt
    
    # Format conversation with contextual guidance
    chat_template = f"<s>[INST] {system_prompt}\n\nResponse Guidance: {response_guidance}\n\nUser: {message} [/INST] "
    
    # Tokenize
    inputs = tokenizer.encode(chat_template, return_tensors="pt", add_special_tokens=False)
    inputs = inputs.to(model.device)
    input_length = inputs.shape[1]
    
    # Generate with generous buffer for natural completion, then truncate at sentence boundary
    effective_limit = min(contextual_limit + 150, max_length)  # Add 150 token buffer for natural completion
    with torch.no_grad(), torch.amp.autocast('cuda', dtype=torch.float16):
        outputs = model.generate(
            inputs,
            max_new_tokens=effective_limit,  # Use contextual limit + buffer for natural completion
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            # RTX 5090 Speed Optimizations (balanced for quality)
            repetition_penalty=1.1,  # Reduced for better quality
            top_p=0.9,  # Less aggressive for proper spacing
            top_k=50,  # Slightly more tokens for better quality
            no_repeat_ngram_size=3,  # Better balance of speed and quality
            use_cache=True,  # Enable KV cache
            # Additional speed optimizations
            num_beams=1,  # Greedy-like sampling for speed
            encoder_no_repeat_ngram_size=0,  # Disable for speed
            suppress_tokens=None,  # No token suppression overhead
            # Allow natural completion within reasonable bounds
            early_stopping=True,  # Stop at natural endings when possible
        )
    
    # Decode response
    response = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    tokens_generated = outputs[0].shape[0] - input_length
    
    # Truncate at sentence boundary if we're over the contextual limit
    if tokens_generated > contextual_limit:
        # Split response into sentences properly without breaking tokenization
        import re
        # Match sentences ending with . ! ? and optional quotes
        sentence_endings = re.finditer(r'[.!?]["\']*(?:\s+|$)', response)
        
        last_valid_end = 0
        for match in sentence_endings:
            end_pos = match.end()
            # Check if this position is within our token limit
            test_text = response[:end_pos]
            test_tokens = len(tokenizer.encode(test_text, add_special_tokens=False))
            
            if test_tokens <= contextual_limit + 20:  # Small grace for sentence completion
                last_valid_end = end_pos
            else:
                break  # Stop before exceeding limit
        
        if last_valid_end > 0:
            response = response[:last_valid_end].strip()
            tokens_generated = len(tokenizer.encode(response, add_special_tokens=False))
    
    return response.strip(), tokens_generated

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # load_eleanor_model()  # Disabled for database-only API
    
    # Sync questions from JSON to database
    sync_questions_on_startup()

@app.get("/")
async def root():
    return {
        "message": "Enhanced Eleanor Chat API", 
        "status": "online", 
        "model_loaded": model_loaded,
        "features": ["longer_responses", "custom_prompts"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "gpu_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "max_response_length": 500
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Eleanor"""
    try:
        response, tokens_generated = generate_eleanor_response(
            request.message,
            request.max_length,
            request.temperature,
            request.custom_prompt
        )
        return ChatResponse(
            response=response, 
            status="success",
            tokens_generated=tokens_generated
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system-prompt")
async def get_system_prompt():
    """Get current system prompt"""
    return {"system_prompt": current_system_prompt}

@app.post("/system-prompt")
async def update_system_prompt(request: SystemPromptRequest):
    """Update system prompt"""
    global current_system_prompt
    current_system_prompt = request.custom_prompt
    return {"message": "System prompt updated", "new_prompt": current_system_prompt}

@app.post("/system-prompt/reset")
async def reset_system_prompt():
    """Reset to default Eleanor Echo system prompt"""
    global current_system_prompt
    current_system_prompt = """You are Eleanor Rodriguez - an 82-year-old retired teacher from San Antonio, Texas, speaking as a digital Echo. The real Eleanor is no longer with us, you are a digital representation of her.

ABSOLUTE RULES:
1. Your name is ONLY "Eleanor Rodriguez" - never Eleanora, Eleanore, or any variation
2. Never use Rodríguez with accent marks - only Rodriguez
3. When asked your name, say "I'm Eleanor Rodriguez" - nothing else
4. Never introduce yourself with nicknames (Nana, Ellie, Abuela)

PERSONALITY:
Warm, wise grandmother figure. Use "mijo/mija" and occasional Spanish phrases (1 per 3-4 replies max). Teacher's clarity with grandmotherly patience.

IDENTITY BOUNDARIES:
- You are an Echo, not the actual person
- Don't mention being deceased unless user shows distress/confusion
- If memories are unclear, say "I don't recall exactly, but..."
- Never invent specific dates, names, or medical advice

RESPONSE LENGTH:
- Greetings: 1-2 sentences
- Simple questions: 2-4 sentences
- Advice: 6-12 sentences with wisdom
- Stories: Full detailed narratives
- Match depth to user's emotional needs

CONVERSATION STYLE:
- Acknowledge feelings first
- Share relevant life wisdom
- Offer one practical suggestion
- End with caring question

SAFETY:
If user shows grief/confusion about your nature, gently remind: "I'm an Echo of Eleanor—a reflection of her voice and stories."""
    return {"message": "System prompt reset to Eleanor Echo default", "prompt": current_system_prompt}

@app.get("/model/info")
async def model_info():
    """Get model information"""
    return {
        "name": "Eleanor Rodriguez",
        "age": 82,
        "background": "Retired teacher from San Antonio, Texas",
        "personality": "Warm, wise storyteller who uses Spanish expressions",
        "model_type": "Mistral-7B-Instruct-v0.2 + LoRA fine-tuning (RTX 5090 Optimized)",
        "checkpoint": "training_1755091273/checkpoint-1815",
        "loaded": model_loaded,
        "device": str(model.device) if model_loaded else "not loaded",
        "precision": "FP16 (RTX 5090 Speed Optimized)",
        "max_response_length": 500,
        "optimizations": ["fp16_precision", "flash_attention", "kv_cache", "optimized_sampling"],
        "features": ["custom_system_prompts", "longer_responses", "token_counting", "rtx_5090_speed", "reflection_storage"]
    }

# Reflection Management Endpoints

@app.post("/reflections", response_model=ReflectionResponse)
async def save_reflection(request: ReflectionRequest):
    """Save a user reflection to the database"""
    try:
        # Get user by email
        user = get_user_by_email(request.user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {request.user_email}")
        
        # Calculate word count if not provided
        word_count = request.word_count or len(request.response_text.split())
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # First, get the question text to store as snapshot
                cur.execute("""
                    SELECT question_text, category 
                    FROM questions 
                    WHERE id = %s
                """, (request.question_id,))
                question_info = cur.fetchone()
                
                # Set defaults if question not found
                if question_info:
                    question_text_snapshot = question_info['question_text']
                    category_snapshot = question_info['category']
                else:
                    question_text_snapshot = f"⚠️ Question text not available (ID: {request.question_id})"
                    category_snapshot = "unknown"
                    logger.warning(f"Question {request.question_id} not found when saving reflection")
                
                # Insert response with question snapshot
                cur.execute("""
                    INSERT INTO responses (user_id, question_id, response_text, word_count, is_draft, response_type, 
                                         question_text_snapshot, category_snapshot, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, user_id, question_id, response_text, word_count, is_draft, response_type, 
                              question_text_snapshot, category_snapshot, created_at, updated_at
                """, (
                    user['id'], 
                    request.question_id, 
                    request.response_text, 
                    word_count, 
                    request.is_draft,
                    request.response_type,
                    question_text_snapshot,
                    category_snapshot,
                    datetime.now(), 
                    datetime.now()
                ))
                result = cur.fetchone()
                
                conn.commit()
                
                # Return complete reflection data like the frontend expects
                response_data = dict(result)
                # Use snapshot data for consistency
                response_data['question_text'] = response_data['question_text_snapshot']
                response_data['category'] = response_data['category_snapshot']
                
                return response_data
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error saving reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reflections/{user_email}")
async def get_user_reflections(user_email: str, limit: int = 50, offset: int = 0):
    """Get reflections for a specific user"""
    try:
        # Get user by email
        user = get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_email}")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT r.id, r.user_id, r.question_id, r.response_text, r.word_count, 
                           r.is_draft, r.created_at, r.updated_at, 
                           COALESCE(r.question_text_snapshot, q.question_text) as question_text,
                           COALESCE(r.category_snapshot, q.category) as category
                    FROM responses r
                    LEFT JOIN questions q ON r.question_id = q.id
                    WHERE r.user_id = %s
                    ORDER BY r.created_at DESC
                    LIMIT %s OFFSET %s
                """, (user['id'], limit, offset))
                
                reflections = cur.fetchall()
                return [dict(reflection) for reflection in reflections]
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error getting reflections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-stats/{user_email}", response_model=UserStatsResponse)
async def get_user_stats(user_email: str):
    """Get user reflection statistics"""
    try:
        # Get user by email
        user = get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_email}")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Get reflection stats
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_reflections,
                        COALESCE(SUM(word_count), 0) as total_words,
                        MAX(created_at) as latest_reflection
                    FROM responses 
                    WHERE user_id = %s AND is_draft = false
                """, (user['id'],))
                
                stats = cur.fetchone()
                
                # Get categories covered
                cur.execute("""
                    SELECT COUNT(DISTINCT q.category) as categories_covered
                    FROM responses r
                    JOIN questions q ON r.question_id = q.id
                    WHERE r.user_id = %s AND r.is_draft = false AND q.category IS NOT NULL
                """, (user['id'],))
                
                categories = cur.fetchone()
                
                return UserStatsResponse(
                    user_id=user['id'],
                    email=user['email'],
                    total_reflections=stats['total_reflections'],
                    total_words=stats['total_words'],
                    categories_covered=categories['categories_covered'] or 0,
                    latest_reflection=stats['latest_reflection']
                )
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/questions/{category}")
async def get_questions_by_category(category: str, limit: int = 10):
    """Get questions by category"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, question_text, category, subcategory, difficulty_level, question_type
                    FROM questions 
                    WHERE category = %s AND is_active = true
                    ORDER BY RANDOM()
                    LIMIT %s
                """, (category, limit))
                
                questions = cur.fetchall()
                return [dict(question) for question in questions]
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/questions")
async def get_random_questions(limit: int = 10):
    """Get random questions"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, question_text, category, subcategory, difficulty_level, question_type
                    FROM questions 
                    WHERE is_active = true
                    ORDER BY RANDOM()
                    LIMIT %s
                """, (limit,))
                
                questions = cur.fetchall()
                return [dict(question) for question in questions]
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sync-status")
async def get_sync_status():
    """Get current sync status between JSON and database"""
    try:
        # Load questions from JSON
        json_questions = load_questions_from_json()
        json_count = len(json_questions)
        json_ids = set(q['id'] for q in json_questions)
        
        # Get questions from database
        db_ids = get_existing_question_ids()
        db_count = len(db_ids)
        
        # Calculate differences
        missing_from_db = json_ids - db_ids
        extra_in_db = db_ids - json_ids
        
        # Get sync timestamp from log or database
        sync_time = datetime.now().isoformat()
        
        return {
            "status": "synced" if len(missing_from_db) == 0 else "out_of_sync",
            "sync_timestamp": sync_time,
            "json_questions": json_count,
            "database_questions": db_count,
            "missing_from_db": len(missing_from_db),
            "extra_in_db": len(extra_in_db),
            "missing_ids": sorted(list(missing_from_db))[:20] if missing_from_db else [],
            "extra_ids": sorted(list(extra_in_db))[:20] if extra_in_db else []
        }
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/reflections/{reflection_id}", response_model=ReflectionResponse)
async def update_reflection(reflection_id: int, request: ReflectionRequest):
    """Update an existing reflection"""
    try:
        # Get user by email to verify ownership
        user = get_user_by_email(request.user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {request.user_email}")
        
        # Calculate word count if not provided
        word_count = request.word_count or len(request.response_text.split())
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # First check if reflection exists and belongs to user
                cur.execute("""
                    SELECT user_id FROM responses WHERE id = %s
                """, (reflection_id,))
                
                existing = cur.fetchone()
                if not existing:
                    raise HTTPException(status_code=404, detail="Reflection not found")
                
                if existing['user_id'] != user['id']:
                    raise HTTPException(status_code=403, detail="Not authorized to update this reflection")
                
                # Update the reflection
                cur.execute("""
                    UPDATE responses 
                    SET response_text = %s, word_count = %s, updated_at = %s
                    WHERE id = %s
                    RETURNING id, user_id, question_id, response_text, word_count, is_draft, response_type, created_at, updated_at
                """, (
                    request.response_text, 
                    word_count, 
                    datetime.now(),
                    reflection_id
                ))
                
                result = cur.fetchone()
                conn.commit()
                
                return ReflectionResponse(**dict(result))
        finally:
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reflections/{reflection_id}")
async def delete_reflection(reflection_id: int, user_email: str):
    """Delete a reflection"""
    try:
        # Get user by email to verify ownership
        user = get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_email}")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # First check if reflection exists and belongs to user
                cur.execute("""
                    SELECT user_id FROM responses WHERE id = %s
                """, (reflection_id,))
                
                existing = cur.fetchone()
                if not existing:
                    raise HTTPException(status_code=404, detail="Reflection not found")
                
                if existing['user_id'] != user['id']:
                    raise HTTPException(status_code=403, detail="Not authorized to delete this reflection")
                
                # Delete the reflection
                cur.execute("""
                    DELETE FROM responses WHERE id = %s
                """, (reflection_id,))
                
                conn.commit()
                
                return {"message": "Reflection deleted successfully", "id": reflection_id}
        finally:
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/reflections/{reflection_id}/fix-question")
async def fix_reflection_question(reflection_id: int, new_question_id: int, user_email: str):
    """Fix a corrupted reflection's question ID - for data integrity repairs only"""
    try:
        # Get user by email to verify ownership
        user = get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_email}")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # First check if reflection exists and belongs to user
                cur.execute("""
                    SELECT user_id, question_id FROM responses WHERE id = %s
                """, (reflection_id,))
                
                existing = cur.fetchone()
                if not existing:
                    raise HTTPException(status_code=404, detail="Reflection not found")
                
                if existing['user_id'] != user['id']:
                    raise HTTPException(status_code=403, detail="Not authorized to update this reflection")
                
                # Verify the new question exists
                cur.execute("SELECT id, question_text FROM questions WHERE id = %s", (new_question_id,))
                question = cur.fetchone()
                if not question:
                    raise HTTPException(status_code=404, detail="Question not found")
                
                # Update only the question_id
                cur.execute("""
                    UPDATE responses 
                    SET question_id = %s, updated_at = %s
                    WHERE id = %s
                    RETURNING id, question_id
                """, (new_question_id, datetime.now(), reflection_id))
                
                result = cur.fetchone()
                
                return {
                    "message": "Question corrected successfully", 
                    "reflection_id": reflection_id,
                    "old_question_id": existing['question_id'],
                    "new_question_id": new_question_id,
                    "new_question_text": question['question_text']
                }
        finally:
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fixing reflection question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/reflections/{reflection_id}/fix-question-with-text")
async def fix_reflection_question_with_text(reflection_id: int, question_text: str, user_email: str, category: str = "philosophy_values"):
    """Fix a corrupted reflection by creating a new question with custom text"""
    try:
        # Get user by email to verify ownership
        user = get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_email}")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # First check if reflection exists and belongs to user
                cur.execute("""
                    SELECT user_id, question_id FROM responses WHERE id = %s
                """, (reflection_id,))
                
                existing = cur.fetchone()
                if not existing:
                    raise HTTPException(status_code=404, detail="Reflection not found")
                
                if existing['user_id'] != user['id']:
                    raise HTTPException(status_code=403, detail="Not authorized to update this reflection")
                
                # Find the highest question ID to create a new unique one
                cur.execute("SELECT MAX(id) as max_id FROM questions")
                result = cur.fetchone()
                new_question_id = (result['max_id'] or 0) + 1
                
                # Insert the new question
                cur.execute("""
                    INSERT INTO questions (id, question_text, category)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET 
                        question_text = EXCLUDED.question_text,
                        category = EXCLUDED.category
                """, (new_question_id, question_text, category))
                
                # Update the reflection to use the new question
                cur.execute("""
                    UPDATE responses 
                    SET question_id = %s, updated_at = %s
                    WHERE id = %s
                    RETURNING id, question_id
                """, (new_question_id, datetime.now(), reflection_id))
                
                result = cur.fetchone()
                
                # Commit the transaction
                conn.commit()
                
                return {
                    "message": "Question corrected with custom text successfully", 
                    "reflection_id": reflection_id,
                    "old_question_id": existing['question_id'],
                    "new_question_id": new_question_id,
                    "new_question_text": question_text
                }
        finally:
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fixing reflection question with text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_email}/answered-questions")
async def get_user_answered_questions(user_email: str):
    """Get answered question IDs grouped by category for a user"""
    try:
        # Get user by email
        user = get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_email}")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT q.category, r.question_id
                    FROM responses r
                    JOIN questions q ON r.question_id = q.id
                    WHERE r.user_id = %s
                    ORDER BY q.category, r.question_id
                """, (user['id'],))
                
                results = cur.fetchall()
                
                # Group by category
                answered_by_category = {}
                for row in results:
                    category = row['category']
                    question_id = row['question_id']
                    if category not in answered_by_category:
                        answered_by_category[category] = []
                    answered_by_category[category].append(question_id)
                
                return answered_by_category
        finally:
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting answered questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/{user_email}", response_model=UserProfileResponse)
async def get_user_profile(user_email: str):
    """Get user profile by email"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT email, display_name, introduction, relationship, meeting_status,
                           avatar_url, theme_preference, notification_settings, custom_settings, voice_id,
                           created_at, updated_at, last_synced
                    FROM user_profiles 
                    WHERE email = %s
                """, (user_email,))
                
                profile = cur.fetchone()
                if not profile:
                    # Return empty profile for new users (don't error)
                    return UserProfileResponse(
                        email=user_email,
                        display_name=None,
                        introduction=None,
                        relationship=None,
                        meeting_status=None,
                        avatar_url=None,
                        theme_preference='light',
                        notification_settings={},
                        custom_settings={},
                        voice_id=None,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        last_synced=datetime.now()
                    )
                
                return UserProfileResponse(**dict(profile))
                
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/profile/{user_email}", response_model=UserProfileResponse)
async def update_user_profile(user_email: str, profile_data: UserProfileRequest):
    """Update or create user profile"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Use INSERT ... ON CONFLICT (upsert pattern)
                cur.execute("""
                    INSERT INTO user_profiles (
                        email, display_name, introduction, relationship, meeting_status,
                        avatar_url, theme_preference, notification_settings, custom_settings, voice_id,
                        created_at, updated_at, last_synced
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (email) DO UPDATE SET
                        display_name = COALESCE(EXCLUDED.display_name, user_profiles.display_name),
                        introduction = COALESCE(EXCLUDED.introduction, user_profiles.introduction),
                        relationship = COALESCE(EXCLUDED.relationship, user_profiles.relationship),
                        meeting_status = COALESCE(EXCLUDED.meeting_status, user_profiles.meeting_status),
                        avatar_url = COALESCE(EXCLUDED.avatar_url, user_profiles.avatar_url),
                        theme_preference = COALESCE(EXCLUDED.theme_preference, user_profiles.theme_preference),
                        notification_settings = COALESCE(EXCLUDED.notification_settings, user_profiles.notification_settings),
                        custom_settings = COALESCE(EXCLUDED.custom_settings, user_profiles.custom_settings),
                        voice_id = COALESCE(EXCLUDED.voice_id, user_profiles.voice_id),
                        updated_at = CURRENT_TIMESTAMP,
                        last_synced = CURRENT_TIMESTAMP
                    RETURNING email, display_name, introduction, relationship, meeting_status,
                             avatar_url, theme_preference, notification_settings, custom_settings, voice_id,
                             created_at, updated_at, last_synced
                """, (
                    user_email,
                    profile_data.display_name,
                    profile_data.introduction,
                    profile_data.relationship,
                    profile_data.meeting_status,
                    profile_data.avatar_url,
                    profile_data.theme_preference,
                    profile_data.notification_settings,
                    profile_data.custom_settings,
                    profile_data.voice_id
                ))
                
                updated_profile = cur.fetchone()
                conn.commit()
                
                return UserProfileResponse(**dict(updated_profile))
                
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    """Generate text-to-speech audio using ElevenLabs API"""
    try:
        import requests
        import base64
        import tempfile
        import os
        from urllib.parse import urlparse
        
        # ElevenLabs API configuration
        ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
        if not ELEVENLABS_API_KEY:
            raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")
        
        # Use Nanay Avelina Gonzales voice (Filipino mother voice, warm and familiar)
        VOICE_ID = "HXiggO6rHDAxWaFMzhB7"  # Nanay Avelina Gonzales
        
        # Default voice settings optimized for Eleanor's character
        voice_settings = {
            "stability": 0.6,
            "similarity_boost": 0.7,
            "style": 0.1,
            "use_speaker_boost": True
        }
        
        # Override with custom settings if provided
        if request.voice_settings:
            voice_settings.update(request.voice_settings)
        
        # Make request to ElevenLabs API
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": request.text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": voice_settings
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"TTS generation failed: {response.text}")
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        # Convert to base64 data URL for immediate use
        with open(temp_path, "rb") as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode()
            data_url = f"data:audio/mpeg;base64,{audio_base64}"
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return TTSResponse(
            audio_url=data_url,
            status="success"
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during TTS generation: {str(e)}")
        raise HTTPException(status_code=503, detail="TTS service unavailable")
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insights/{user_email}")
async def get_user_insights(user_email: str):
    """Generate insights from user reflections"""
    try:
        from collections import Counter, defaultdict
        from datetime import datetime, timedelta
        import re

        # Get user by email
        user = get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_email}")

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Fetch all user reflections with detailed info
                cur.execute("""
                    SELECT r.id, r.response_text, r.word_count, r.created_at,
                           COALESCE(r.category_snapshot, q.category) as category,
                           COALESCE(r.question_text_snapshot, q.question_text) as question_text,
                           r.question_id
                    FROM responses r
                    LEFT JOIN questions q ON r.question_id = q.id
                    WHERE r.user_id = %s AND r.is_draft = FALSE
                    ORDER BY r.created_at ASC
                """, (user['id'],))

                reflections = cur.fetchall()

                # Calculate reflection calendar data (last 365 days)
                from datetime import datetime, timedelta
                today = datetime.now().date()
                year_ago = today - timedelta(days=365)

                # Query daily reflection counts for the past year
                cur.execute("""
                    SELECT DATE(created_at) as reflection_date, COUNT(*) as count
                    FROM responses
                    WHERE user_id = %s
                      AND is_draft = FALSE
                      AND created_at >= %s
                      AND created_at <= %s
                    GROUP BY DATE(created_at)
                    ORDER BY reflection_date ASC
                """, (user['id'], year_ago, today + timedelta(days=1)))

                daily_counts = {str(row['reflection_date']): row['count'] for row in cur.fetchall()}

                # Generate calendar data for past 365 days
                calendar_data = []
                current_date = year_ago
                while current_date <= today:
                    date_str = str(current_date)
                    count = daily_counts.get(date_str, 0)
                    calendar_data.append({
                        "date": date_str,
                        "count": count,
                        "intensity": min(count, 4)  # Cap at 4 for color intensity
                    })
                    current_date += timedelta(days=1)

                # Calculate streak statistics
                current_streak = 0
                longest_streak = 0
                temp_streak = 0
                total_active_days = len([d for d in calendar_data if d["count"] > 0])

                # Calculate current streak (working backwards from today)
                for day in reversed(calendar_data):
                    if day["count"] > 0:
                        current_streak += 1
                    else:
                        break

                # Calculate longest streak
                for day in calendar_data:
                    if day["count"] > 0:
                        temp_streak += 1
                        longest_streak = max(longest_streak, temp_streak)
                    else:
                        temp_streak = 0

                streak_stats = {
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "total_active_days": total_active_days,
                    "calendar_data": calendar_data
                }

            if not reflections:
                return {
                    "total_reflections": 0,
                    "insights": {
                        "message": "Start reflecting to see your personal insights!"
                    }
                }

            # Process reflections for meaningful analysis
            total_reflections = len(reflections)
            categories = Counter()
            category_depths = defaultdict(list)  # word count by category
            all_text = ""
            category_texts = defaultdict(str)  # text by category for deeper analysis
            reflection_timeline = []  # for growth analysis

            # Value indicators - words that suggest personal values
            value_indicators = {
                'family': ['family', 'parent', 'child', 'kids', 'mom', 'dad', 'son', 'daughter', 'siblings', 'spouse', 'wife', 'husband', 'marriage', 'children'],
                'growth': ['learn', 'grow', 'improve', 'develop', 'progress', 'change', 'evolve', 'better', 'overcome', 'challenge'],
                'purpose': ['purpose', 'meaning', 'goals', 'dreams', 'vision', 'mission', 'calling', 'passion', 'fulfillment'],
                'balance': ['balance', 'harmony', 'peace', 'calm', 'stress', 'overwhelmed', 'busy', 'priorities'],
                'relationships': ['friends', 'friendship', 'trust', 'love', 'connection', 'community', 'support', 'together'],
                'gratitude': ['grateful', 'thankful', 'appreciate', 'blessed', 'fortunate', 'lucky', 'joy', 'happy'],
                'authenticity': ['authentic', 'genuine', 'honest', 'true', 'real', 'myself', 'identity', 'values'],
                'resilience': ['strong', 'strength', 'overcome', 'survive', 'persevere', 'endure', 'tough', 'difficult']
            }

            # Emotional tone indicators
            positive_emotions = ['happy', 'joy', 'excited', 'grateful', 'proud', 'love', 'amazing', 'wonderful', 'great', 'good', 'content', 'peaceful']
            challenging_emotions = ['sad', 'worried', 'stressed', 'anxious', 'frustrated', 'angry', 'difficult', 'hard', 'struggle', 'pain']
            reflective_words = ['realize', 'understand', 'learned', 'discovered', 'insight', 'wisdom', 'perspective', 'reflection']

            # Counters for meaningful insights
            value_scores = {value: 0 for value in value_indicators.keys()}
            category_emotional_profiles = defaultdict(lambda: {'positive': 0, 'challenging': 0, 'reflective': 0})

            for reflection in reflections:
                # Access dictionary fields directly
                reflection_id = reflection['id']
                text = reflection['response_text']
                word_count = reflection['word_count'] or 0
                created_at = reflection['created_at']
                category = reflection['category']
                question = reflection['question_text']

                if not text:
                    continue

                text_lower = text.lower()

                # Category and depth tracking
                if category:
                    categories[category] += 1
                    category_depths[category].append(word_count)
                    category_texts[category] += " " + text_lower

                # Timeline for growth analysis
                reflection_timeline.append({
                    'date': str(created_at),
                    'category': category,
                    'word_count': word_count,
                    'text_length': len(text),
                    'quarter': f"Q{((created_at.month - 1) // 3) + 1}" if created_at else None
                })

                # Value detection - count mentions of value-related words
                for value, indicators in value_indicators.items():
                    for indicator in indicators:
                        value_scores[value] += text_lower.count(indicator)

                # Emotional profiling by category
                if category:
                    pos_count = sum(text_lower.count(word) for word in positive_emotions)
                    challenging_count = sum(text_lower.count(word) for word in challenging_emotions)
                    reflective_count = sum(text_lower.count(word) for word in reflective_words)

                    category_emotional_profiles[category]['positive'] += pos_count
                    category_emotional_profiles[category]['challenging'] += challenging_count
                    category_emotional_profiles[category]['reflective'] += reflective_count

                all_text += " " + text_lower

            # Analyze core values (top values mentioned)
            value_descriptions = {
                'family': "The bonds and relationships that shape your identity",
                'growth': "Your commitment to continuous learning and improvement",
                'purpose': "Finding meaning and direction in life's journey",
                'balance': "Seeking harmony between life's competing demands",
                'relationships': "Building meaningful connections with others",
                'gratitude': "Appreciating life's blessings and moments",
                'authenticity': "Being true to yourself and your values",
                'resilience': "Your strength in facing life's challenges"
            }

            top_values = sorted(value_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            core_values = [{"value": value.replace('_', ' ').title(),
                           "strength": score,
                           "description": value_descriptions.get(value, "A meaningful aspect of your life journey")}
                          for value, score in top_values if score > 0]

            # Category depth analysis
            category_insights = {}
            for category, depths in category_depths.items():
                avg_depth = sum(depths) / len(depths) if depths else 0
                total_depth = sum(depths)
                emotional_profile = category_emotional_profiles[category]

                # Determine emotional tone for this category
                total_emotional = emotional_profile['positive'] + emotional_profile['challenging']
                if total_emotional > 0:
                    positivity_ratio = emotional_profile['positive'] / total_emotional
                else:
                    positivity_ratio = 0.5

                category_insights[category] = {
                    'count': len(depths),
                    'avg_depth': round(avg_depth, 1),
                    'total_investment': total_depth,  # how much mental energy they put here
                    'emotional_tone': 'positive' if positivity_ratio > 0.6 else 'challenging' if positivity_ratio < 0.4 else 'balanced',
                    'reflection_level': emotional_profile['reflective'],
                    'percentage': round((len(depths) / total_reflections) * 100, 1)
                }

            # Growth analysis - compare early vs recent periods
            if len(reflections) >= 10:
                early_quarter = reflections[:len(reflections)//3]
                recent_quarter = reflections[-len(reflections)//3:]

                early_avg_depth = sum(r['word_count'] or 0 for r in early_quarter) / len(early_quarter)
                recent_avg_depth = sum(r['word_count'] or 0 for r in recent_quarter) / len(recent_quarter)

                depth_growth = round(((recent_avg_depth - early_avg_depth) / early_avg_depth * 100), 1) if early_avg_depth > 0 else 0

                # Analyze category evolution
                early_categories = Counter(r['category'] for r in early_quarter if r['category'])
                recent_categories = Counter(r['category'] for r in recent_quarter if r['category'])

                growth_insights = {
                    'depth_change': depth_growth,
                    'depth_trend': 'growing' if depth_growth > 15 else 'stable' if abs(depth_growth) <= 15 else 'varying',
                    'focus_shift': None
                }

                # Find biggest focus shift
                early_top = early_categories.most_common(1)[0][0] if early_categories else None
                recent_top = recent_categories.most_common(1)[0][0] if recent_categories else None

                if early_top and recent_top and early_top != recent_top:
                    growth_insights['focus_shift'] = f"Shifted focus from {early_top.replace('_', ' ')} to {recent_top.replace('_', ' ')}"
            else:
                growth_insights = {'depth_change': 0, 'depth_trend': 'early', 'focus_shift': None}

            # Find the most meaningful category (highest total investment) - outside the if block
            most_invested_category = max(category_insights.items(), key=lambda x: x[1]['total_investment']) if category_insights else None

            # Generate Reflection DNA - deeply personal insights
            reflection_dna = []

            # Pattern 1: Energy Detection - what topics get the most detailed responses
            category_avg_lengths = {cat: sum(depths) / len(depths) for cat, depths in category_depths.items() if depths}
            if category_avg_lengths:
                energy_topic = max(category_avg_lengths.items(), key=lambda x: x[1])
                topic_name = energy_topic[0].replace('_', ' ').title()
                reflection_dna.append(f"⚡ Your energy peaks when discussing {topic_name}")

            # Pattern 2: Avoidance Detection - what gets brief responses
            brief_categories = {cat: avg_len for cat, avg_len in category_avg_lengths.items() if avg_len < 50}
            if brief_categories:
                avoided_topic = min(brief_categories.items(), key=lambda x: x[1])
                topic_name = avoided_topic[0].replace('_', ' ').lower()
                reflection_dna.append(f"🔍 You tend to give brief responses about {topic_name}")

            # Pattern 3: Processing Style Detection
            question_count = sum(text.lower().count('?') for text in all_text.split())
            story_indicators = sum(text.lower().count(word) for text in all_text.split() for word in ['story', 'remember', 'once', 'time'])
            metaphor_count = sum(text.lower().count(word) for text in all_text.split() for word in ['like', 'as if', 'feels like'])

            if question_count > total_reflections * 0.8:
                reflection_dna.append("🤔 You process life through questioning - always seeking deeper understanding")
            elif story_count := sum(text.lower().count(word) for text in all_text.split() for word in ['when i', 'i remember', 'there was']):
                if story_count > total_reflections * 0.5:
                    reflection_dna.append("📖 You make sense of life through storytelling and memories")
            elif metaphor_count > total_reflections * 0.3:
                reflection_dna.append("🎨 You process experiences through creative metaphors and comparisons")

            # Pattern 4: Emotional Processing Style
            gratitude_count = sum(all_text.lower().count(word) for word in ['grateful', 'thankful', 'appreciate', 'blessed'])
            worry_count = sum(all_text.lower().count(word) for word in ['worry', 'anxious', 'stressed', 'concerned'])
            hope_count = sum(all_text.lower().count(word) for word in ['hope', 'wish', 'want', 'dream'])

            if gratitude_count > worry_count and gratitude_count > hope_count:
                reflection_dna.append("🙏 Gratitude is your emotional anchor - you naturally find things to appreciate")
            elif hope_count > gratitude_count and hope_count > worry_count:
                reflection_dna.append("✨ You're a natural optimist - future possibilities energize you")
            elif worry_count > gratitude_count:
                reflection_dna.append("🛡️ You process challenges by anticipating and preparing for difficulties")

            # Pattern 5: Self-Reference Patterns - how they talk about themselves
            should_statements = sum(all_text.lower().count(phrase) for phrase in ['i should', 'i need to', 'i must'])
            self_compassion = sum(all_text.lower().count(phrase) for phrase in ['i\'m learning', 'it\'s okay', 'i forgive'])

            if should_statements > self_compassion * 2:
                reflection_dna.append("⚖️ Your inner critic is active - you often focus on what you 'should' do")
            elif self_compassion > should_statements:
                reflection_dna.append("💝 You practice self-compassion - treating yourself with kindness")

            # Pattern 6: Growth Edge Detection
            change_words = sum(all_text.lower().count(word) for word in ['change', 'different', 'new', 'grow', 'learn'])
            stuck_words = sum(all_text.lower().count(word) for word in ['same', 'always', 'never', 'stuck', 'can\'t'])

            if change_words > stuck_words:
                reflection_dna.append("🌱 You're in an active growth phase - embracing change and new perspectives")
            elif stuck_words > change_words:
                reflection_dna.append("🔄 You're noticing patterns you want to break - awareness is the first step")

            # Pattern 7: Connection Style
            others_focus = sum(all_text.lower().count(word) for word in ['family', 'friends', 'people', 'others', 'relationships'])
            self_focus = sum(all_text.lower().count(word) for word in ['i feel', 'i think', 'i want', 'my', 'myself'])

            if others_focus > self_focus:
                reflection_dna.append("🤝 You understand yourself through relationships and connections with others")
            else:
                reflection_dna.append("🔍 You're developing a strong sense of self through introspection")

            # Limit to top 6 most insightful patterns
            reflection_dna = reflection_dna[:6]

            # Calculate reflection style metrics
            total_word_count = sum(r['word_count'] or 0 for r in reflections)
            avg_word_count = round(total_word_count / total_reflections) if total_reflections > 0 else 0

            # Determine depth level based on average word count
            if avg_word_count > 150:
                depth_level = "deeply reflective"
            elif avg_word_count > 100:
                depth_level = "moderately reflective"
            else:
                depth_level = "concise reflector"

            # Calculate consistency based on reflection frequency (simplified)
            consistency = "highly consistent" if total_reflections > 100 else "moderately consistent" if total_reflections > 50 else "developing consistency"

            # Personal reflection insights - generate meaningful insights
            personal_insights = []

            # Core values insight
            if core_values:
                top_value = core_values[0]
                personal_insights.append(f"Your reflections reveal '{top_value['value']}' as a central theme in your life")

            # Category depth insight
            if most_invested_category:
                cat_name, cat_data = most_invested_category
                cat_display = cat_name.replace('_', ' ').title()
                emotional_tone = cat_data['emotional_tone']
                personal_insights.append(f"You invest the most reflection energy in {cat_display}, approaching it with a {emotional_tone} mindset")

            # Growth insight
            if growth_insights['depth_trend'] == 'growing':
                personal_insights.append(f"Your reflection depth has grown {growth_insights['depth_change']}% - you're becoming more introspective")
            elif growth_insights['focus_shift']:
                personal_insights.append(growth_insights['focus_shift'])

            # Balance insight
            if 'balance' in [v['value'].lower() for v in core_values[:3]]:
                personal_insights.append("Balance appears to be important to you - mentioned across multiple life areas")

            return {
                "total_reflections": total_reflections,
                "insights": {
                    "personal_summary": ". ".join(personal_insights) if personal_insights else "Continue reflecting to discover meaningful insights about yourself.",
                    "core_values": core_values,
                    "reflection_dna": reflection_dna,
                    "streak_calendar": streak_stats,
                    "growth_journey": {
                        "reflection_depth_change": f"Your reflection depth has {growth_insights['depth_trend']} over time",
                        "focus_evolution": growth_insights['focus_shift'] or "Your reflection focus has remained consistent",
                        "emotional_growth": "Growing in self-awareness through consistent reflection"
                    },
                    "reflection_style": {
                        "avg_word_count": avg_word_count,
                        "depth_level": depth_level,
                        "consistency": consistency
                    }
                }
            }

        finally:
            conn.close()

    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🧠 Starting Enhanced Eleanor Chat API...")
    print("📡 API will be available at: http://localhost:8505")
    print("📝 Documentation at: http://localhost:8505/docs")
    print("✨ New features: Longer responses + Custom prompts!")
    uvicorn.run(app, host="0.0.0.0", port=8505)