import { createClient } from '@supabase/supabase-js'

// Environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL!
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Please check your .env file.')
}

// Create standard Supabase client (with anon key)
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// Database types (will be generated after Supabase setup)
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: number
          auth_id: string
          email: string
          name: string | null
          role: string
          created_at: string
          updated_at: string | null
          is_active: boolean
          last_login_at: string | null
          secondary_roles: string[] | null
          image: string | null
          reset_token: string | null
          cultural_background: string[] | null
          primary_role: string | null
          email_verified: string | null
          crisis_contact_info: Record<string, any> | null
          grief_support_opt_in: boolean
          memorial_account: boolean
          memorial_contact_id: number | null
          is_admin: boolean
          failed_login_attempts: number
          locked_until: string | null
          reset_token_expires: string | null
          important_people: Record<string, any> | null
          birthday: string | null
          significant_events: Record<string, any> | null
          admin_role_id: string | null
          last_shadow_session: string | null
          privacy_preferences: Record<string, any> | null
        }
        Insert: {
          auth_id: string
          email: string
          name?: string | null
          role?: string
          is_active?: boolean
          secondary_roles?: string[] | null
          image?: string | null
          cultural_background?: string[] | null
          primary_role?: string | null
          crisis_contact_info?: Record<string, any> | null
          grief_support_opt_in?: boolean
          memorial_account?: boolean
          memorial_contact_id?: number | null
          is_admin?: boolean
          failed_login_attempts?: number
          important_people?: Record<string, any> | null
          birthday?: string | null
          significant_events?: Record<string, any> | null
          admin_role_id?: string | null
          privacy_preferences?: Record<string, any> | null
        }
        Update: {
          name?: string | null
          role?: string
          is_active?: boolean
          last_login_at?: string | null
          secondary_roles?: string[] | null
          image?: string | null
          cultural_background?: string[] | null
          primary_role?: string | null
          email_verified?: string | null
          crisis_contact_info?: Record<string, any> | null
          grief_support_opt_in?: boolean
          memorial_account?: boolean
          memorial_contact_id?: number | null
          is_admin?: boolean
          failed_login_attempts?: number
          locked_until?: string | null
          important_people?: Record<string, any> | null
          birthday?: string | null
          significant_events?: Record<string, any> | null
          admin_role_id?: string | null
          privacy_preferences?: Record<string, any> | null
        }
      }
      reflections: {
        Row: {
          id: number
          user_id: number
          question_id: number
          response_text: string
          word_count: number
          is_draft: boolean
          created_at: string
          updated_at: string | null
          response_type: string
          emotional_tags: string[] | null
          privacy_level: string
          voice_notes: Record<string, any> | null
          shared_with: number[] | null
          revision_count: number
          original_response_id: number | null
          ai_analysis: Record<string, any> | null
          sentiment_score: number | null
          themes: string[] | null
          follow_up_questions: string[] | null
          memory_strength: number | null
          context_tags: string[] | null
        }
        Insert: {
          user_id: number
          question_id: number
          response_text: string
          word_count?: number
          is_draft?: boolean
          response_type?: string
          emotional_tags?: string[] | null
          privacy_level?: string
          voice_notes?: Record<string, any> | null
          shared_with?: number[] | null
          revision_count?: number
          original_response_id?: number | null
          ai_analysis?: Record<string, any> | null
          sentiment_score?: number | null
          themes?: string[] | null
          follow_up_questions?: string[] | null
          memory_strength?: number | null
          context_tags?: string[] | null
        }
        Update: {
          response_text?: string
          word_count?: number
          is_draft?: boolean
          response_type?: string
          emotional_tags?: string[] | null
          privacy_level?: string
          voice_notes?: Record<string, any> | null
          shared_with?: number[] | null
          revision_count?: number
          ai_analysis?: Record<string, any> | null
          sentiment_score?: number | null
          themes?: string[] | null
          follow_up_questions?: string[] | null
          memory_strength?: number | null
          context_tags?: string[] | null
        }
      }
      questions: {
        Row: {
          id: number
          question_text: string
          category: string
          subcategory: string | null
          difficulty_level: number
          is_active: boolean
          created_at: string
          updated_at: string | null
          tags: string[] | null
          context_info: Record<string, any> | null
          follow_up_prompts: string[] | null
          estimated_time_minutes: number | null
          requires_preparation: boolean
          emotional_intensity: number | null
          age_appropriateness: string | null
          cultural_sensitivity: string[] | null
          therapeutic_value: number | null
          memory_type: string | null
          recommended_frequency: string | null
        }
        Insert: {
          question_text: string
          category: string
          subcategory?: string | null
          difficulty_level?: number
          is_active?: boolean
          tags?: string[] | null
          context_info?: Record<string, any> | null
          follow_up_prompts?: string[] | null
          estimated_time_minutes?: number | null
          requires_preparation?: boolean
          emotional_intensity?: number | null
          age_appropriateness?: string | null
          cultural_sensitivity?: string[] | null
          therapeutic_value?: number | null
          memory_type?: string | null
          recommended_frequency?: string | null
        }
        Update: {
          question_text?: string
          category?: string
          subcategory?: string | null
          difficulty_level?: number
          is_active?: boolean
          tags?: string[] | null
          context_info?: Record<string, any> | null
          follow_up_prompts?: string[] | null
          estimated_time_minutes?: number | null
          requires_preparation?: boolean
          emotional_intensity?: number | null
          age_appropriateness?: string | null
          cultural_sensitivity?: string[] | null
          therapeutic_value?: number | null
          memory_type?: string | null
          recommended_frequency?: string | null
        }
      }
      user_profiles: {
        Row: {
          id: number
          user_id: number
          display_name: string | null
          relationship: string | null
          meeting_status: string | null
          introduction: string | null
          voice_id: string | null
          created_at: string
          updated_at: string | null
          avatar_url: string | null
          bio: string | null
          interests: string[] | null
          goals: string[] | null
          reflection_preferences: Record<string, any> | null
          notification_settings: Record<string, any> | null
          privacy_settings: Record<string, any> | null
          cultural_preferences: Record<string, any> | null
          accessibility_settings: Record<string, any> | null
          time_zone: string | null
          preferred_language: string | null
        }
        Insert: {
          user_id: number
          display_name?: string | null
          relationship?: string | null
          meeting_status?: string | null
          introduction?: string | null
          voice_id?: string | null
          avatar_url?: string | null
          bio?: string | null
          interests?: string[] | null
          goals?: string[] | null
          reflection_preferences?: Record<string, any> | null
          notification_settings?: Record<string, any> | null
          privacy_settings?: Record<string, any> | null
          cultural_preferences?: Record<string, any> | null
          accessibility_settings?: Record<string, any> | null
          time_zone?: string | null
          preferred_language?: string | null
        }
        Update: {
          display_name?: string | null
          relationship?: string | null
          meeting_status?: string | null
          introduction?: string | null
          voice_id?: string | null
          avatar_url?: string | null
          bio?: string | null
          interests?: string[] | null
          goals?: string[] | null
          reflection_preferences?: Record<string, any> | null
          notification_settings?: Record<string, any> | null
          privacy_settings?: Record<string, any> | null
          cultural_preferences?: Record<string, any> | null
          accessibility_settings?: Record<string, any> | null
          time_zone?: string | null
          preferred_language?: string | null
        }
      }
      ai_conversations: {
        Row: {
          id: number
          user_id: number
          user_message: string
          ai_response: string
          conversation_type: string
          model_version: string | null
          created_at: string
          response_time_ms: number | null
          tokens_used: number | null
          satisfaction_rating: number | null
          context_data: Record<string, any> | null
          follow_up_suggestions: string[] | null
          emotional_tone: string | null
          conversation_thread_id: string | null
        }
        Insert: {
          user_id: number
          user_message: string
          ai_response: string
          conversation_type: string
          model_version?: string | null
          response_time_ms?: number | null
          tokens_used?: number | null
          satisfaction_rating?: number | null
          context_data?: Record<string, any> | null
          follow_up_suggestions?: string[] | null
          emotional_tone?: string | null
          conversation_thread_id?: string | null
        }
        Update: {
          satisfaction_rating?: number | null
          context_data?: Record<string, any> | null
          follow_up_suggestions?: string[] | null
          emotional_tone?: string | null
        }
      }
      voice_profiles: {
        Row: {
          id: number
          user_id: number
          voice_id: string
          voice_name: string | null
          provider: string
          is_active: boolean
          created_at: string
          updated_at: string | null
          voice_settings: Record<string, any> | null
          sample_audio_url: string | null
          clone_quality_score: number | null
          training_status: string | null
          training_data_url: string | null
          usage_count: number
          last_used_at: string | null
        }
        Insert: {
          user_id: number
          voice_id: string
          voice_name?: string | null
          provider: string
          is_active?: boolean
          voice_settings?: Record<string, any> | null
          sample_audio_url?: string | null
          clone_quality_score?: number | null
          training_status?: string | null
          training_data_url?: string | null
          usage_count?: number
        }
        Update: {
          voice_name?: string | null
          is_active?: boolean
          voice_settings?: Record<string, any> | null
          sample_audio_url?: string | null
          clone_quality_score?: number | null
          training_status?: string | null
          training_data_url?: string | null
          usage_count?: number
          last_used_at?: string | null
        }
      }
      training_datasets: {
        Row: {
          id: number
          user_id: number
          dataset_name: string
          dataset_type: string
          file_path: string | null
          file_size_mb: number | null
          record_count: number | null
          created_at: string
          updated_at: string | null
          processing_status: string | null
          quality_score: number | null
          metadata: Record<string, any> | null
          is_active: boolean
          export_format: string | null
          compression_ratio: number | null
          validation_results: Record<string, any> | null
        }
        Insert: {
          user_id: number
          dataset_name: string
          dataset_type: string
          file_path?: string | null
          file_size_mb?: number | null
          record_count?: number | null
          processing_status?: string | null
          quality_score?: number | null
          metadata?: Record<string, any> | null
          is_active?: boolean
          export_format?: string | null
          compression_ratio?: number | null
          validation_results?: Record<string, any> | null
        }
        Update: {
          dataset_name?: string
          dataset_type?: string
          file_path?: string | null
          file_size_mb?: number | null
          record_count?: number | null
          processing_status?: string | null
          quality_score?: number | null
          metadata?: Record<string, any> | null
          is_active?: boolean
          export_format?: string | null
          compression_ratio?: number | null
          validation_results?: Record<string, any> | null
        }
      }
    }
  }
}

// Helper functions for common operations
export const api = {
  // Authentication helpers
  async signUp(email: string, password: string) {
    const siteUrl = import.meta.env.VITE_SITE_URL || window.location.origin;
    return await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${siteUrl}/dashboard`
      }
    })
  },

  async signIn(email: string, password: string) {
    return await supabase.auth.signInWithPassword({ email, password })
  },

  async signInWithGoogle() {
    return await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/dashboard`
      }
    })
  },

  async signOut() {
    return await supabase.auth.signOut()
  },

  async getSession() {
    return await supabase.auth.getSession()
  },

  // User data helpers
  async getCurrentUser() {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return null

    const { data } = await supabase
      .from('users')
      .select('*')
      .eq('auth_id', user.id)
      .single()

    return data
  },

  async createUserRecord(authId: string, email: string, name?: string) {
    return await supabase
      .from('users')
      .insert({
        auth_id: authId,
        email,
        name,
        role: 'user',
        is_active: true
      })
      .select()
      .single()
  },

  // Reflections
  async getReflections(limit = 50, offset = 0) {
    return await supabase
      .from('reflections')
      .select(`
        *,
        questions (
          id,
          question_text,
          category
        )
      `)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1)
  },

  async createReflection(questionId: number, responseText: string, isDraft = false) {
    const user = await this.getCurrentUser()
    if (!user) throw new Error('User not authenticated')

    return await supabase
      .from('reflections')
      .insert({
        user_id: user.id,
        question_id: questionId,
        response_text: responseText,
        word_count: responseText.split(' ').length,
        is_draft: isDraft,
      })
      .select()
      .single()
  },

  // Questions
  async getQuestions(category?: string) {
    let query = supabase
      .from('questions')
      .select('*')
      .eq('is_active', true)
      .order('id')

    if (category) {
      query = query.eq('category', category)
    }

    return await query
  },

  async getQuestionCategories() {
    const { data } = await supabase
      .from('questions')
      .select('category')
      .eq('is_active', true)

    const categories = [...new Set(data?.map(q => q.category))]
    return categories.sort()
  },

  // User profile
  async getUserProfile() {
    const user = await this.getCurrentUser()
    if (!user) return null

    return await supabase
      .from('user_profiles')
      .select('*')
      .eq('user_id', user.id)
      .single()
  },

  async updateUserProfile(updates: Partial<Database['public']['Tables']['user_profiles']['Insert']>) {
    const user = await this.getCurrentUser()
    if (!user) throw new Error('User not authenticated')

    return await supabase
      .from('user_profiles')
      .upsert({ user_id: user.id, ...updates })
      .select()
      .single()
  },

  // Password management
  async resetPasswordForEmail(email: string, redirectTo?: string) {
    const baseUrl = window.location.origin
    const defaultRedirectTo = `${baseUrl}/reset-password`

    return await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: redirectTo || defaultRedirectTo,
    })
  },

  async updatePassword(newPassword: string) {
    return await supabase.auth.updateUser({
      password: newPassword
    })
  },

  async verifyPasswordResetToken(accessToken: string, refreshToken: string) {
    return await supabase.auth.setSession({
      access_token: accessToken,
      refresh_token: refreshToken
    })
  },

  // Get password reset info from URL parameters (both query string and hash fragment)
  getPasswordResetTokensFromUrl(): { accessToken: string; refreshToken: string; type: string } | null {
    // First try query parameters
    let urlParams = new URLSearchParams(window.location.search)
    let accessToken = urlParams.get('access_token')
    let refreshToken = urlParams.get('refresh_token')
    let type = urlParams.get('type')

    // If not found in query params, try hash fragment (common with OAuth flows)
    if (!accessToken && window.location.hash) {
      urlParams = new URLSearchParams(window.location.hash.substring(1))
      accessToken = urlParams.get('access_token')
      refreshToken = urlParams.get('refresh_token')
      type = urlParams.get('type')
    }

    if (accessToken && refreshToken && type === 'recovery') {
      return { accessToken, refreshToken, type }
    }

    return null
  },

  // Settings management
  async getUserSettings() {
    const user = await this.getCurrentUser()
    if (!user) return null

    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('notification_settings, reflection_preferences')
        .eq('user_id', user.id)
        .single()

      if (error) {
        console.warn('Settings fetch failed:', error)
        return null
      }

      // Combine both settings objects into a single settings object
      const settings = {
        ...(data?.reflection_preferences || {}),
        ...(data?.notification_settings || {})
      }

      return Object.keys(settings).length > 0 ? settings : null
    } catch (error) {
      console.warn('Error fetching user settings:', error)
      return null
    }
  },

  async updateUserSettings(settings: Record<string, any>) {
    const user = await this.getCurrentUser()
    if (!user) throw new Error('User not authenticated')

    try {
      // Split settings into appropriate categories
      const { theme, ...notificationSettings } = settings

      // Prepare the update object
      const updateData: any = {}

      // Theme goes into reflection_preferences
      if (theme !== undefined) {
        updateData.reflection_preferences = { theme }
      }

      // All other settings go into notification_settings
      if (Object.keys(notificationSettings).length > 0) {
        updateData.notification_settings = notificationSettings
      }

      const { data, error } = await supabase
        .from('user_profiles')
        .upsert({
          user_id: user.id,
          ...updateData
        })
        .select()
        .single()

      if (error) {
        console.error('Settings save failed:', error)
        throw error
      }

      return data
    } catch (error) {
      console.error('Error updating user settings:', error)
      throw error
    }
  }
}

export default supabase