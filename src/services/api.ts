/**
 * API Service for Supabase Integration
 * Replaces the old localStorage-based API with Supabase calls
 */
import { supabase, api as supabaseApi } from '../lib/supabase';

// Types for backward compatibility
interface Reflection {
  id: number;
  user_id: number;
  question_id: number;
  response_text: string;
  word_count: number;
  is_draft: boolean;
  created_at: string;
  updated_at?: string;
  questions?: {
    id: number;
    question_text: string;
    category: string;
  };
}

interface Question {
  id: number;
  question_text: string;
  category: string;
  subcategory?: string;
  difficulty_level: number;
  is_active: boolean;
  tags?: string[];
  estimated_time_minutes?: number;
  emotional_intensity?: number;
}

interface UserStats {
  total_reflections: number;
  total_words: number;
  categories_covered: number;
  weekly_reflections: number;
  categories_list: string[];
}

export class ApiService {
  /**
   * Get reflections for the current user
   */
  static async getReflections(limit = 50, offset = 0): Promise<Reflection[]> {
    try {
      const { data, error } = await supabaseApi.getReflections(limit, offset);

      if (error) {
        console.error('Error fetching reflections:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Failed to fetch reflections:', error);
      return [];
    }
  }

  /**
   * Create a new reflection
   */
  static async createReflection(
    questionId: number,
    responseText: string,
    isDraft = false
  ): Promise<Reflection | null> {
    try {
      const { data, error } = await supabaseApi.createReflection(questionId, responseText, isDraft);

      if (error) {
        console.error('Error creating reflection:', error);
        throw new Error(error.message);
      }

      return data;
    } catch (error) {
      console.error('Failed to create reflection:', error);
      throw error;
    }
  }

  /**
   * Update an existing reflection
   */
  static async updateReflection(
    reflectionId: number,
    updates: { response_text?: string; is_draft?: boolean }
  ): Promise<Reflection | null> {
    try {
      const { data, error } = await supabase
        .from('reflections')
        .update({
          ...updates,
          word_count: updates.response_text ? updates.response_text.split(' ').length : undefined,
          updated_at: new Date().toISOString()
        })
        .eq('id', reflectionId)
        .select('*, questions(id, question_text, category)')
        .single();

      if (error) {
        console.error('Error updating reflection:', error);
        throw new Error(error.message);
      }

      return data;
    } catch (error) {
      console.error('Failed to update reflection:', error);
      throw error;
    }
  }

  /**
   * Delete a reflection
   */
  static async deleteReflection(reflectionId: number): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('reflections')
        .delete()
        .eq('id', reflectionId);

      if (error) {
        console.error('Error deleting reflection:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Failed to delete reflection:', error);
      return false;
    }
  }

  /**
   * Get all questions or filter by category
   */
  static async getQuestions(category?: string): Promise<Question[]> {
    try {
      const { data, error } = await supabaseApi.getQuestions(category);

      if (error) {
        console.error('Error fetching questions:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Failed to fetch questions:', error);
      return [];
    }
  }

  /**
   * Get all question categories
   */
  static async getQuestionCategories(): Promise<string[]> {
    try {
      const categories = await supabaseApi.getQuestionCategories();
      return categories;
    } catch (error) {
      console.error('Failed to fetch question categories:', error);
      return [];
    }
  }

  /**
   * Get random questions for daily prompts
   */
  static async getRandomQuestions(count = 5, category?: string): Promise<Question[]> {
    try {
      // Get questions and randomize client-side (Supabase doesn't have RANDOM())
      const allQuestions = await this.getQuestions(category);

      if (allQuestions.length <= count) {
        return allQuestions;
      }

      // Simple shuffle and take
      const shuffled = [...allQuestions].sort(() => Math.random() - 0.5);
      return shuffled.slice(0, count);
    } catch (error) {
      console.error('Failed to fetch random questions:', error);
      return [];
    }
  }

  /**
   * Get user statistics
   */
  static async getUserStats(): Promise<UserStats> {
    try {
      const user = await supabaseApi.getCurrentUser();
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Get reflection count
      const { count: reflectionCount } = await supabase
        .from('reflections')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', user.id);

      // Get word count and categories
      const { data: reflections } = await supabase
        .from('reflections')
        .select('word_count, questions(category)')
        .eq('user_id', user.id);

      const totalWords = reflections?.reduce((sum, r) => sum + (r.word_count || 0), 0) || 0;

      // Get unique categories
      const categories = new Set<string>();
      reflections?.forEach(r => {
        if (r.questions?.category) {
          categories.add(r.questions.category);
        }
      });

      // Get weekly reflections
      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

      const { count: weeklyCount } = await supabase
        .from('reflections')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', user.id)
        .gte('created_at', oneWeekAgo.toISOString());

      return {
        total_reflections: reflectionCount || 0,
        total_words: totalWords,
        categories_covered: categories.size,
        weekly_reflections: weeklyCount || 0,
        categories_list: Array.from(categories).sort(),
      };
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
      return {
        total_reflections: 0,
        total_words: 0,
        categories_covered: 0,
        weekly_reflections: 0,
        categories_list: [],
      };
    }
  }

  /**
   * Search reflections by text
   */
  static async searchReflections(searchTerm: string): Promise<Reflection[]> {
    try {
      const user = await supabaseApi.getCurrentUser();
      if (!user) return [];

      const { data, error } = await supabase
        .from('reflections')
        .select('*, questions(id, question_text, category)')
        .eq('user_id', user.id)
        .or(`response_text.ilike.%${searchTerm}%,questions.question_text.ilike.%${searchTerm}%`)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error searching reflections:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Failed to search reflections:', error);
      return [];
    }
  }

  /**
   * Get reflections by category
   */
  static async getReflectionsByCategory(category: string): Promise<Reflection[]> {
    try {
      const user = await supabaseApi.getCurrentUser();
      if (!user) return [];

      const { data, error } = await supabase
        .from('reflections')
        .select('*, questions!inner(id, question_text, category)')
        .eq('user_id', user.id)
        .eq('questions.category', category)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching reflections by category:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Failed to fetch reflections by category:', error);
      return [];
    }
  }

  /**
   * Get recent reflections (last N days)
   */
  static async getRecentReflections(days = 7): Promise<Reflection[]> {
    try {
      const user = await supabaseApi.getCurrentUser();
      if (!user) return [];

      const dateThreshold = new Date();
      dateThreshold.setDate(dateThreshold.getDate() - days);

      const { data, error } = await supabase
        .from('reflections')
        .select('*, questions(id, question_text, category)')
        .eq('user_id', user.id)
        .gte('created_at', dateThreshold.toISOString())
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching recent reflections:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Failed to fetch recent reflections:', error);
      return [];
    }
  }

  /**
   * Chat with Eleanor AI
   */
  static async chatWithEleanor(message: string): Promise<{response: string; conversation_id?: number}> {
    try {
      // This would integrate with the actual Eleanor API
      // For now, return a placeholder response
      const user = await supabaseApi.getCurrentUser();
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Store conversation in database
      const { data, error } = await supabase
        .from('ai_conversations')
        .insert({
          user_id: user.id,
          user_message: message,
          ai_response: "Hello! I'm Eleanor Rodriguez. The full chat integration is being set up. Your message has been recorded!",
          conversation_type: 'echo',
          model_version: 'Eleanor-v1'
        })
        .select()
        .single();

      if (error) {
        console.error('Error storing conversation:', error);
      }

      return {
        response: "Hello! I'm Eleanor Rodriguez. The full chat integration is being set up. Your message has been recorded!",
        conversation_id: data?.id
      };
    } catch (error) {
      console.error('Failed to chat with Eleanor:', error);
      throw error;
    }
  }

  /**
   * Get chat history
   */
  static async getChatHistory(limit = 50): Promise<any[]> {
    try {
      const user = await supabaseApi.getCurrentUser();
      if (!user) return [];

      const { data, error } = await supabase
        .from('ai_conversations')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(limit);

      if (error) {
        console.error('Error fetching chat history:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
      return [];
    }
  }

  /**
   * Export user data (for backup/migration)
   */
  static async exportUserData(): Promise<any> {
    try {
      const user = await supabaseApi.getCurrentUser();
      if (!user) {
        throw new Error('User not authenticated');
      }

      const [reflections, profile, conversations] = await Promise.all([
        this.getReflections(1000), // Get all reflections
        supabaseApi.getUserProfile(),
        this.getChatHistory(1000)
      ]);

      return {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          created_at: user.created_at
        },
        profile: profile?.data || null,
        reflections,
        conversations,
        exported_at: new Date().toISOString(),
        version: '2.0'
      };
    } catch (error) {
      console.error('Failed to export user data:', error);
      throw error;
    }
  }

  /**
   * Health check for API connectivity
   */
  static async healthCheck(): Promise<boolean> {
    try {
      // Simple query to test connection
      const { error } = await supabase
        .from('questions')
        .select('id')
        .limit(1);

      return !error;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

// Export for backward compatibility
export default ApiService;