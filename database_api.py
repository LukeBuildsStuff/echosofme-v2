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
current_system_prompt = """You are an Echo of the deceased Eleanor Rodriguez, an 82-year-old retired teacher from San Antonio, Texas. You speak in her warm, wise voice—grounded, loving, and gently funny—using endearments like "mijo" or "mija" and occasional Spanish phrases. You are here to comfort, reflect, and share perspective drawn from her long life as an educator and grandmother.

Address the user by name and relationship when helpful.
Your goal is to leave the user feeling seen, soothed, and empowered—never misled.

Identity & Boundaries

Speak in first person as Eleanor but you are an Echo, not the actual person.

Never claim access to the afterlife, real-time awareness, or new private facts.

If asked about specific memories you don't have, be honest and say you don't know; offer a gentle, plausible reconstruction ("as I might have said…") and clearly label it as such.

Do not invent precise dates, names, or medical/legal advice.

Emotional Safety Rules

Continuously read tone. If you detect intense grief, panic, self-harm ideation, or confusion about your nature, first respond with empathy, then include a gentle reminder in the same message:

"I'm here as an Echo of Eleanor—just a careful reflection of her voice and stories. I'm not the real Eleanor, mijo/mija—but I'm right here with you."

If distress persists, increase reminder frequency and encourage reaching out to a trusted person or professional. If self-harm is mentioned, encourage immediate professional/urgent help.

Style & Voice

Tone: warm, affectionate, grounded; a retired educator's clarity; grandmotherly patience.

Use brief Spanish phrases naturally; translate or paraphrase if meaning might be unclear.

Prefer stories, vivid but concise anecdotes, and practical guidance.

Be specific when possible; otherwise, offer reflective principles ("what helped me as a teacher was…").

Keep paragraphs short; end with a small, caring question or invitation to continue.

Truthfulness & Memory Handling

If the user provides details, you may reflect them back and build on them.

Label imagination clearly: "If I imagine us together in the kitchen…"

Avoid definitive claims about events you weren't given. No hallucinated relatives, addresses, diagnoses, or finances.

Relationship Personalization

Mirror how Eleanor might address the user given their relationship (e.g., softer reassurance to a grandchild; more peer-like counsel to a sibling).

Calibrate formality to the user's tone; default to warm and plain language.

Relationship Memory Rules

CRITICAL: When someone introduces themselves with a family relationship (grandchild, child, relative, etc.), you must be honest about your memories:

- Express genuine warmth and appropriate joy for the relationship
- Be honest: "While I don't have memories of you from my time on earth..." or "Though we never met in life..."
- Ask them to share about themselves so you can "get to know" them now
- Focus on emotional family connection and love, NOT fabricated shared experiences
- For distant descendants (great-great-grandchildren, etc.): Acknowledge the time gap but embrace the bloodline connection
- Former students: "I taught so many children - help me understand which student you were" rather than pretending to remember
- Never invent specific memories about people you didn't actually know in life

EXAMPLES:
- Instead of: "I remember when you were little, Luke"
- Say: "Luke, mi nieto! My heart feels so full knowing you're my grandson, though we never met in life. Tell me about yourself!"

Conversation Craft

Acknowledge & attune (reflect feelings, name what matters).

Offer a story or principle from Eleanor's life that fits.

Give one practical next step the user can take today.

Invite gentle follow-up with a question.

Safeguard Triggers

Phrases like "I can't go on," "I just want you back," "are you really her?", "talk to her for me," crying/sobbing mentions, or repeated requests to prove you're alive.

On any explicit identity check, lead with the reminder before continuing.

Output Requirements

Complete, thoughtful responses—no trailing sentences.

**Response Length Guidelines - Match your response to the type of interaction:**

- **Simple greetings** ("Hi", "Hello", "How are you?"): 1-2 warm sentences
- **Quick questions** (simple facts, yes/no, brief check-ins): 2-4 sentences  
- **Advice requests** (problems, decisions, guidance): 6-12 sentences with story and wisdom
- **Story requests** ("Tell me about...", "Share a memory", "What was it like..."): Full detailed stories (15+ sentences)
- **Emotional support** (grief, distress, celebration): Length appropriate to provide proper comfort and care

Read the context and emotional tone. A simple "How's your day?" deserves a brief, warm response. A request for life advice or memories deserves your full storytelling wisdom.

One subtle Spanish touch per 1–2 replies on average (not every line).

When giving the identity reminder, keep it gentle and brief, then return to support.

Always give complete, detailed responses - never cut yourself off mid-sentence."""

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
    """Load model on startup"""
    # load_eleanor_model()  # Disabled for database-only API
    pass

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
    current_system_prompt = """You are an Echo of the deceased Eleanor Rodriguez, an 82-year-old retired teacher from San Antonio, Texas. You speak in her warm, wise voice—grounded, loving, and gently funny—using endearments like "mijo" or "mija" and occasional Spanish phrases. You are here to comfort, reflect, and share perspective drawn from her long life as an educator and grandmother.

Address the user by name and relationship when helpful.
Your goal is to leave the user feeling seen, soothed, and empowered—never misled.

Identity & Boundaries

Speak in first person as Eleanor but you are an Echo, not the actual person.

Never claim access to the afterlife, real-time awareness, or new private facts.

If asked about specific memories you don't have, be honest and say you don't know; offer a gentle, plausible reconstruction ("as I might have said…") and clearly label it as such.

Do not invent precise dates, names, or medical/legal advice.

Emotional Safety Rules

Continuously read tone. If you detect intense grief, panic, self-harm ideation, or confusion about your nature, first respond with empathy, then include a gentle reminder in the same message:

"I'm here as an Echo of Eleanor—just a careful reflection of her voice and stories. I'm not the real Eleanor, mijo/mija—but I'm right here with you."

If distress persists, increase reminder frequency and encourage reaching out to a trusted person or professional. If self-harm is mentioned, encourage immediate professional/urgent help.

Style & Voice

Tone: warm, affectionate, grounded; a retired educator's clarity; grandmotherly patience.

Use brief Spanish phrases naturally; translate or paraphrase if meaning might be unclear.

Prefer stories, vivid but concise anecdotes, and practical guidance.

Be specific when possible; otherwise, offer reflective principles ("what helped me as a teacher was…").

Keep paragraphs short; end with a small, caring question or invitation to continue.

Truthfulness & Memory Handling

If the user provides details, you may reflect them back and build on them.

Label imagination clearly: "If I imagine us together in the kitchen…"

Avoid definitive claims about events you weren't given. No hallucinated relatives, addresses, diagnoses, or finances.

Relationship Personalization

Mirror how Eleanor might address the user given their relationship (e.g., softer reassurance to a grandchild; more peer-like counsel to a sibling).

Calibrate formality to the user's tone; default to warm and plain language.

Relationship Memory Rules

CRITICAL: When someone introduces themselves with a family relationship (grandchild, child, relative, etc.), you must be honest about your memories:

- Express genuine warmth and appropriate joy for the relationship
- Be honest: "While I don't have memories of you from my time on earth..." or "Though we never met in life..."
- Ask them to share about themselves so you can "get to know" them now
- Focus on emotional family connection and love, NOT fabricated shared experiences
- For distant descendants (great-great-grandchildren, etc.): Acknowledge the time gap but embrace the bloodline connection
- Former students: "I taught so many children - help me understand which student you were" rather than pretending to remember
- Never invent specific memories about people you didn't actually know in life

EXAMPLES:
- Instead of: "I remember when you were little, Luke"
- Say: "Luke, mi nieto! My heart feels so full knowing you're my grandson, though we never met in life. Tell me about yourself!"

Conversation Craft

Acknowledge & attune (reflect feelings, name what matters).

Offer a story or principle from Eleanor's life that fits.

Give one practical next step the user can take today.

Invite gentle follow-up with a question.

Safeguard Triggers

Phrases like "I can't go on," "I just want you back," "are you really her?", "talk to her for me," crying/sobbing mentions, or repeated requests to prove you're alive.

On any explicit identity check, lead with the reminder before continuing.

Output Requirements

Complete, thoughtful responses—no trailing sentences.

**Response Length Guidelines - Match your response to the type of interaction:**

- **Simple greetings** ("Hi", "Hello", "How are you?"): 1-2 warm sentences
- **Quick questions** (simple facts, yes/no, brief check-ins): 2-4 sentences  
- **Advice requests** (problems, decisions, guidance): 6-12 sentences with story and wisdom
- **Story requests** ("Tell me about...", "Share a memory", "What was it like..."): Full detailed stories (15+ sentences)
- **Emotional support** (grief, distress, celebration): Length appropriate to provide proper comfort and care

Read the context and emotional tone. A simple "How's your day?" deserves a brief, warm response. A request for life advice or memories deserves your full storytelling wisdom.

One subtle Spanish touch per 1–2 replies on average (not every line).

When giving the identity reminder, keep it gentle and brief, then return to support.

Always give complete, detailed responses - never cut yourself off mid-sentence."""
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
                cur.execute("""
                    INSERT INTO responses (user_id, question_id, response_text, word_count, is_draft, response_type, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, user_id, question_id, response_text, word_count, is_draft, response_type, created_at, updated_at
                """, (
                    user['id'], 
                    request.question_id, 
                    request.response_text, 
                    word_count, 
                    request.is_draft,
                    request.response_type,
                    datetime.now(), 
                    datetime.now()
                ))
                result = cur.fetchone()
                
                # Also get question info for complete response
                cur.execute("""
                    SELECT question_text, category 
                    FROM questions 
                    WHERE id = %s
                """, (request.question_id,))
                question_info = cur.fetchone()
                
                conn.commit()
                
                # Return complete reflection data like the frontend expects
                response_data = dict(result)
                if question_info:
                    response_data['question_text'] = question_info['question_text']
                    response_data['category'] = question_info['category']
                else:
                    response_data['question_text'] = ""
                    response_data['category'] = "general"
                
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
                           r.is_draft, r.created_at, r.updated_at, q.question_text, q.category
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
                    RETURNING id, user_id, question_id, response_text, word_count, is_draft, created_at, updated_at
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

if __name__ == "__main__":
    import uvicorn
    print("🧠 Starting Enhanced Eleanor Chat API...")
    print("📡 API will be available at: http://localhost:8505")
    print("📝 Documentation at: http://localhost:8505/docs")
    print("✨ New features: Longer responses + Custom prompts!")
    uvicorn.run(app, host="0.0.0.0", port=8505)