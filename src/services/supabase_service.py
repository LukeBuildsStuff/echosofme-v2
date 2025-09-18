"""
Supabase service for backend operations
Handles database operations using Supabase Python client
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import logging

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseService:
    """Service class for Supabase database operations"""

    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")  # Backend only

        if not self.supabase_url or not self.supabase_service_key:
            raise ValueError(
                "Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables."
            )

        self.client: Client = create_client(self.supabase_url, self.supabase_service_key)
        logger.info("✅ Supabase service initialized")

    # User Management
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            result = self.client.table('users').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    def get_user_by_auth_id(self, auth_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Supabase auth ID"""
        try:
            result = self.client.table('users').select('*').eq('auth_id', auth_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user by auth_id {auth_id}: {e}")
            return None

    def create_user(self, auth_id: str, email: str, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new user record"""
        try:
            user_data = {
                'auth_id': auth_id,
                'email': email,
                'name': name,
                'role': 'user',
                'is_active': True
            }

            result = self.client.table('users').insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            return None

    def update_user(self, user_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user record"""
        try:
            result = self.client.table('users').update(updates).eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None

    # Reflection Management
    def get_user_reflections(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get reflections for a user with question details"""
        try:
            result = self.client.table('reflections')\
                .select('*, questions(id, question_text, category)')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .offset(offset)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting reflections for user {user_id}: {e}")
            return []

    def create_reflection(self, user_id: int, question_id: int, response_text: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new reflection"""
        try:
            reflection_data = {
                'user_id': user_id,
                'question_id': question_id,
                'response_text': response_text,
                'word_count': len(response_text.split()),
                'is_draft': kwargs.get('is_draft', False),
                'response_type': kwargs.get('response_type', 'reflection'),
                'emotional_tags': kwargs.get('emotional_tags', []),
                'privacy_level': kwargs.get('privacy_level', 'private')
            }

            result = self.client.table('reflections').insert(reflection_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating reflection: {e}")
            return None

    def update_reflection(self, reflection_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a reflection"""
        try:
            # Update word count if response_text is being updated
            if 'response_text' in updates:
                updates['word_count'] = len(updates['response_text'].split())

            result = self.client.table('reflections').update(updates).eq('id', reflection_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating reflection {reflection_id}: {e}")
            return None

    def delete_reflection(self, reflection_id: int, user_id: int) -> bool:
        """Delete a reflection (with user ownership check)"""
        try:
            result = self.client.table('reflections')\
                .delete()\
                .eq('id', reflection_id)\
                .eq('user_id', user_id)\
                .execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting reflection {reflection_id}: {e}")
            return False

    # Question Management
    def get_questions(self, category: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get questions, optionally filtered by category"""
        try:
            query = self.client.table('questions').select('*').eq('is_active', True)

            if category:
                query = query.eq('category', category)

            result = query.order('id').limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting questions: {e}")
            return []

    def get_question_categories(self) -> List[str]:
        """Get all unique question categories"""
        try:
            result = self.client.table('questions')\
                .select('category')\
                .eq('is_active', True)\
                .execute()

            categories = list(set(row['category'] for row in result.data if row['category']))
            return sorted(categories)
        except Exception as e:
            logger.error(f"Error getting question categories: {e}")
            return []

    def get_random_questions(self, count: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get random questions for daily prompts"""
        try:
            # Note: Supabase doesn't have RANDOM() function like PostgreSQL
            # We'll get questions and randomize client-side for now
            # In production, consider using a stored procedure or function
            questions = self.get_questions(category, limit=count * 3)  # Get more to randomize

            import random
            if len(questions) <= count:
                return questions

            return random.sample(questions, count)
        except Exception as e:
            logger.error(f"Error getting random questions: {e}")
            return []

    # User Statistics
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            # Total reflections with count
            reflections_result = self.client.table('reflections')\
                .select('*', count='exact')\
                .eq('user_id', user_id)\
                .execute()

            total_reflections = reflections_result.count or 0

            # Get reflections for word count and categories
            reflections_data = self.client.table('reflections')\
                .select('word_count, questions(category)')\
                .eq('user_id', user_id)\
                .execute()

            total_words = sum(r.get('word_count', 0) for r in reflections_data.data)

            # Categories covered
            categories = set()
            for r in reflections_data.data:
                if r.get('questions') and r['questions'].get('category'):
                    categories.add(r['questions']['category'])

            # Streak calculation (simplified - last 7 days)
            from datetime import datetime, timedelta
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

            recent_result = self.client.table('reflections')\
                .select('created_at', count='exact')\
                .eq('user_id', user_id)\
                .gte('created_at', seven_days_ago)\
                .execute()

            weekly_reflections = recent_result.count or 0

            return {
                'total_reflections': total_reflections,
                'total_words': total_words,
                'categories_covered': len(categories),
                'weekly_reflections': weekly_reflections,
                'categories_list': sorted(list(categories))
            }
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {
                'total_reflections': 0,
                'total_words': 0,
                'categories_covered': 0,
                'weekly_reflections': 0,
                'categories_list': []
            }

    # User Profile Management
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile data"""
        try:
            result = self.client.table('user_profiles').select('*').eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return None

    def upsert_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create or update user profile"""
        try:
            profile_data['user_id'] = user_id
            result = self.client.table('user_profiles').upsert(profile_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error upserting user profile {user_id}: {e}")
            return None

    # AI Conversations
    def create_ai_conversation(self, user_id: int, message: str, response: str,
                             conversation_type: str = 'echo') -> Optional[Dict[str, Any]]:
        """Create AI conversation record"""
        try:
            conversation_data = {
                'user_id': user_id,
                'user_message': message,
                'ai_response': response,
                'conversation_type': conversation_type,
                'model_version': 'Eleanor-v1'  # Update as needed
            }

            result = self.client.table('ai_conversations').insert(conversation_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating AI conversation: {e}")
            return None

    def get_ai_conversation_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get AI conversation history for user"""
        try:
            result = self.client.table('ai_conversations')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting AI conversation history for {user_id}: {e}")
            return []

    # Insights Data
    def get_user_insights_data(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive data for insights analysis"""
        try:
            from datetime import datetime, timedelta
            from collections import defaultdict

            # Get all non-draft reflections with question details (past 365 days for performance)
            year_ago = (datetime.now() - timedelta(days=365)).isoformat()

            reflections_result = self.client.table('reflections')\
                .select('*, questions(id, question_text, category)')\
                .eq('user_id', user_id)\
                .eq('is_draft', False)\
                .gte('created_at', year_ago)\
                .order('created_at', desc=False)\
                .execute()

            reflections = reflections_result.data

            # Group reflections by date for calendar view
            daily_counts = defaultdict(int)
            for reflection in reflections:
                created_date = reflection['created_at'][:10]  # Extract YYYY-MM-DD
                daily_counts[created_date] += 1

            # Convert to list format for calendar
            calendar_data = []
            for date_str, count in daily_counts.items():
                calendar_data.append({
                    'date': date_str,
                    'count': count,
                    'level': min(count, 4)  # Cap intensity at 4
                })

            return {
                'reflections': reflections,
                'calendar_data': calendar_data,
                'daily_counts': dict(daily_counts)
            }

        except Exception as e:
            logger.error(f"Error getting insights data for user {user_id}: {e}")
            return {
                'reflections': [],
                'calendar_data': [],
                'daily_counts': {}
            }

    # Health Check
    def health_check(self) -> bool:
        """Check if Supabase connection is healthy"""
        try:
            # Simple query to test connection
            result = self.client.table('questions').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False

# Create singleton instance
_supabase_service = None

def get_supabase_service() -> SupabaseService:
    """Get singleton Supabase service instance"""
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service