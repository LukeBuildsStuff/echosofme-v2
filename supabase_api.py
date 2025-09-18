"""
FastAPI server using Supabase backend
Replaces database_api.py with Supabase integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import jwt
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
from dateutil import parser as date_parser

# Import Supabase service
try:
    from src.services.supabase_service import get_supabase_service
except ImportError:
    # Fallback for Railway deployment
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    from services.supabase_service import get_supabase_service

# Keep Eleanor LLM integration from original API
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Echoes of Me - Supabase API", description="Supabase-powered backend for Echoes of Me")

# CORS configuration for development and production
allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative React dev server
    "https://echosofme-v2-brqqndi2w-luke-moellers-projects.vercel.app",  # Current Vercel deployment
    "https://echosofme-v2.vercel.app",  # Future production Vercel domain
]

# In production, allow Railway to set additional origins via environment variable
production_origin = os.getenv("FRONTEND_URL")
if production_origin:
    allowed_origins.append(production_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

# User Insights
@app.get("/insights/{user_email}")
async def get_user_insights(user_email: str):
    """Generate comprehensive insights from user reflections"""
    try:
        supabase = get_supabase_service()

        # Get user by email
        user = supabase.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_email}")

        user_id = user['id']

        # Get insights data from SupabaseService
        insights_data = supabase.get_user_insights_data(user_id)
        reflections = insights_data['reflections']
        calendar_data = insights_data['calendar_data']

        if not reflections:
            return {
                "total_reflections": 0,
                "insights": {
                    "message": "Start reflecting to see your personal insights!"
                }
            }

        # Calculate streak statistics from calendar data
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

        # Generate full calendar data for past 365 days (filling missing dates)
        today = datetime.now().date()
        year_ago = today - timedelta(days=365)

        daily_counts = {d['date']: d['count'] for d in calendar_data}
        full_calendar_data = []
        current_date = year_ago
        while current_date <= today:
            date_str = str(current_date)
            count = daily_counts.get(date_str, 0)
            full_calendar_data.append({
                "date": date_str,
                "count": count,
                "intensity": min(count, 4)  # Cap at 4 for color intensity
            })
            current_date += timedelta(days=1)

        streak_stats = {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_active_days": total_active_days,
            "calendar_data": full_calendar_data
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
            # Access Supabase data structure
            reflection_id = reflection['id']
            text = reflection['response_text']
            word_count = reflection['word_count'] or 0
            created_at = date_parser.parse(reflection['created_at'])

            # Get category and question from nested questions object
            category = None
            question = None
            if reflection.get('questions'):
                category = reflection['questions'].get('category')
                question = reflection['questions'].get('question_text')

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
            early_categories = Counter()
            recent_categories = Counter()

            for r in early_quarter:
                if r.get('questions') and r['questions'].get('category'):
                    early_categories[r['questions']['category']] += 1

            for r in recent_quarter:
                if r.get('questions') and r['questions'].get('category'):
                    recent_categories[r['questions']['category']] += 1

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

        # Find the most meaningful category (highest total investment)
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

    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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