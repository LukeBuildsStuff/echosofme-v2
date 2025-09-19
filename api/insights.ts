import type { VercelRequest, VercelResponse } from '@vercel/node';
import { createClient } from '@supabase/supabase-js';

// Type definitions
interface Reflection {
  id: number;
  response_text: string;
  word_count: number;
  created_at: string;
  questions?: {
    category?: string;
    question_text?: string;
  };
}

interface CoreValue {
  value: string;
  strength: number;
  description: string;
}

interface CategoryInsight {
  count: number;
  avg_depth: number;
  total_investment: number;
  emotional_tone: 'positive' | 'challenging' | 'balanced';
  reflection_level: number;
  percentage: number;
}

interface StreakStats {
  current_streak: number;
  longest_streak: number;
  total_active_days: number;
  calendar_data: Array<{
    date: string;
    count: number;
    intensity: number;
  }>;
}

// Helper function to count occurrences of words in text
function countWords(text: string, words: string[]): number {
  const lowerText = text.toLowerCase();
  return words.reduce((count, word) => count + (lowerText.split(word).length - 1), 0);
}

// Helper function to count specific phrases in text
function countPhrases(text: string, phrases: string[]): number {
  const lowerText = text.toLowerCase();
  return phrases.reduce((count, phrase) => {
    const regex = new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    return count + (lowerText.match(regex) || []).length;
  }, 0);
}

// Calculate calendar data with streak information
function calculateStreakStats(reflections: Reflection[]): StreakStats {
  const dailyCounts: { [date: string]: number } = {};

  // Count reflections per day
  reflections.forEach(reflection => {
    const date = reflection.created_at.split('T')[0]; // Extract YYYY-MM-DD
    dailyCounts[date] = (dailyCounts[date] || 0) + 1;
  });

  // Calculate streaks
  const sortedDates = Object.keys(dailyCounts).sort();
  let currentStreak = 0;
  let longestStreak = 0;
  let tempStreak = 0;

  if (sortedDates.length > 0) {
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

    // Check if current streak is active (today or yesterday)
    if (dailyCounts[today] || dailyCounts[yesterday]) {
      currentStreak = 1;
      let checkDate = new Date();
      checkDate.setDate(checkDate.getDate() - 1);

      while (dailyCounts[checkDate.toISOString().split('T')[0]]) {
        currentStreak++;
        checkDate.setDate(checkDate.getDate() - 1);
      }
    }

    // Calculate longest streak
    for (let i = 0; i < sortedDates.length; i++) {
      const currentDate = new Date(sortedDates[i]);
      const nextDate = i + 1 < sortedDates.length ? new Date(sortedDates[i + 1]) : null;

      tempStreak++;

      if (!nextDate || (nextDate.getTime() - currentDate.getTime()) > 86400000) {
        longestStreak = Math.max(longestStreak, tempStreak);
        tempStreak = 0;
      }
    }
  }

  // Generate calendar data for past year
  const calendarData: Array<{ date: string; count: number; intensity: number }> = [];
  const oneYearAgo = new Date();
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

  let currentDate = new Date(oneYearAgo);
  while (currentDate <= new Date()) {
    const dateStr = currentDate.toISOString().split('T')[0];
    const count = dailyCounts[dateStr] || 0;
    calendarData.push({
      date: dateStr,
      count,
      intensity: Math.min(count, 4) // Cap at 4 for color intensity
    });
    currentDate.setDate(currentDate.getDate() + 1);
  }

  return {
    current_streak: currentStreak,
    longest_streak: longestStreak,
    total_active_days: Object.keys(dailyCounts).length,
    calendar_data: calendarData
  };
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Initialize Supabase client
    const supabaseUrl = process.env.VITE_SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

    if (!supabaseUrl || !supabaseServiceKey) {
      return res.status(500).json({
        error: 'Missing Supabase configuration'
      });
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Get user ID from authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Missing or invalid authorization header' });
    }

    const token = authHeader.substring(7);

    // Verify user and get user ID (simplified - in production you'd verify the JWT)
    // For now, assume the token contains user info or is the user ID
    let userId: number;
    try {
      // This is a simplified approach - in production you'd properly verify the JWT
      const userCheckResponse = await supabase.auth.getUser(token);
      if (userCheckResponse.error || !userCheckResponse.data.user) {
        return res.status(401).json({ error: 'Invalid token' });
      }

      // Get user record from users table
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('id')
        .eq('auth_id', userCheckResponse.data.user.id)
        .single();

      if (userError || !userData) {
        return res.status(404).json({ error: 'User not found' });
      }

      userId = userData.id;
    } catch (error) {
      return res.status(401).json({ error: 'Invalid authorization token' });
    }

    // Fetch user's reflections with question details
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

    const { data: reflections, error: reflectionsError } = await supabase
      .from('reflections')
      .select(`
        id,
        response_text,
        word_count,
        created_at,
        questions (
          id,
          question_text,
          category
        )
      `)
      .eq('user_id', userId)
      .eq('is_draft', false)
      .gte('created_at', oneYearAgo.toISOString())
      .order('created_at', { ascending: false });

    if (reflectionsError) {
      console.error('Supabase error:', reflectionsError);
      return res.status(500).json({ error: 'Failed to fetch reflections' });
    }

    if (!reflections || reflections.length === 0) {
      return res.status(200).json({
        total_reflections: 0,
        insights: {
          personal_summary: "Start reflecting to discover meaningful insights about yourself.",
          core_values: [],
          reflection_dna: [],
          streak_calendar: {
            current_streak: 0,
            longest_streak: 0,
            total_active_days: 0,
            calendar_data: []
          },
          growth_journey: {
            reflection_depth_change: "No reflection data available yet",
            focus_evolution: "Begin your reflection journey to track your growth",
            emotional_growth: "Start reflecting to discover your emotional patterns"
          },
          category_insights: {},
          reflection_style: {
            depth_level: "new reflector",
            consistency: "just getting started",
            total_words: 0,
            avg_words_per_reflection: 0
          }
        }
      });
    }

    // Calculate streak stats
    const streakStats = calculateStreakStats(reflections as Reflection[]);

    // Value indicators - words that suggest personal values
    const valueIndicators = {
      family: ['family', 'parent', 'child', 'kids', 'mom', 'dad', 'son', 'daughter', 'siblings', 'spouse', 'wife', 'husband', 'marriage', 'children'],
      growth: ['learn', 'grow', 'improve', 'develop', 'progress', 'change', 'evolve', 'better', 'overcome', 'challenge'],
      purpose: ['purpose', 'meaning', 'goals', 'dreams', 'vision', 'mission', 'calling', 'passion', 'fulfillment'],
      balance: ['balance', 'harmony', 'peace', 'calm', 'stress', 'overwhelmed', 'busy', 'priorities'],
      relationships: ['friends', 'friendship', 'trust', 'love', 'connection', 'community', 'support', 'together'],
      gratitude: ['grateful', 'thankful', 'appreciate', 'blessed', 'fortunate', 'lucky', 'joy', 'happy'],
      authenticity: ['authentic', 'genuine', 'honest', 'true', 'real', 'myself', 'identity', 'values'],
      resilience: ['strong', 'strength', 'overcome', 'survive', 'persevere', 'endure', 'tough', 'difficult']
    };

    const valueDescriptions = {
      family: "The bonds and relationships that shape your identity",
      growth: "Your commitment to continuous learning and improvement",
      purpose: "Finding meaning and direction in life's journey",
      balance: "Seeking harmony between life's competing demands",
      relationships: "Building meaningful connections with others",
      gratitude: "Appreciating life's blessings and moments",
      authenticity: "Being true to yourself and your values",
      resilience: "Your strength in facing life's challenges"
    };

    // Emotional tone indicators
    const positiveEmotions = ['happy', 'joy', 'excited', 'grateful', 'proud', 'love', 'amazing', 'wonderful', 'great', 'good', 'content', 'peaceful'];
    const challengingEmotions = ['sad', 'worried', 'stressed', 'anxious', 'frustrated', 'angry', 'difficult', 'hard', 'struggle', 'pain'];
    const reflectiveWords = ['realize', 'understand', 'learned', 'discovered', 'insight', 'wisdom', 'perspective', 'reflection'];

    // Process reflections for analysis
    const totalReflections = reflections.length;
    const categories: { [key: string]: number } = {};
    const categoryDepths: { [key: string]: number[] } = {};
    const categoryEmotionalProfiles: { [key: string]: { positive: number; challenging: number; reflective: number } } = {};
    const valueScores: { [key: string]: number } = {};
    let allText = '';

    // Initialize value scores
    Object.keys(valueIndicators).forEach(value => {
      valueScores[value] = 0;
    });

    // Process each reflection
    reflections.forEach((reflection: any) => {
      const text = reflection.response_text || '';
      const wordCount = reflection.word_count || 0;
      const category = reflection.questions?.category;

      if (!text) return;

      const textLower = text.toLowerCase();
      allText += ' ' + textLower;

      // Category tracking
      if (category) {
        categories[category] = (categories[category] || 0) + 1;
        if (!categoryDepths[category]) categoryDepths[category] = [];
        categoryDepths[category].push(wordCount);

        // Emotional profiling by category
        if (!categoryEmotionalProfiles[category]) {
          categoryEmotionalProfiles[category] = { positive: 0, challenging: 0, reflective: 0 };
        }

        categoryEmotionalProfiles[category].positive += countWords(textLower, positiveEmotions);
        categoryEmotionalProfiles[category].challenging += countWords(textLower, challengingEmotions);
        categoryEmotionalProfiles[category].reflective += countWords(textLower, reflectiveWords);
      }

      // Value detection
      Object.entries(valueIndicators).forEach(([value, indicators]) => {
        valueScores[value] += countWords(textLower, indicators);
      });
    });

    // Analyze core values
    const topValues = Object.entries(valueScores)
      .filter(([_, score]) => score > 0)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    const coreValues: CoreValue[] = topValues.map(([value, score]) => ({
      value: value.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      strength: score,
      description: valueDescriptions[value as keyof typeof valueDescriptions] || "A meaningful aspect of your life journey"
    }));

    // Category insights
    const categoryInsights: { [key: string]: CategoryInsight } = {};
    Object.entries(categoryDepths).forEach(([category, depths]) => {
      if (depths.length === 0) return;

      const avgDepth = depths.reduce((a, b) => a + b, 0) / depths.length;
      const totalDepth = depths.reduce((a, b) => a + b, 0);
      const emotionalProfile = categoryEmotionalProfiles[category] || { positive: 0, challenging: 0, reflective: 0 };

      const totalEmotional = emotionalProfile.positive + emotionalProfile.challenging;
      const positivityRatio = totalEmotional > 0 ? emotionalProfile.positive / totalEmotional : 0.5;

      let emotionalTone: 'positive' | 'challenging' | 'balanced' = 'balanced';
      if (positivityRatio > 0.6) emotionalTone = 'positive';
      else if (positivityRatio < 0.4) emotionalTone = 'challenging';

      categoryInsights[category] = {
        count: depths.length,
        avg_depth: Math.round(avgDepth * 10) / 10,
        total_investment: totalDepth,
        emotional_tone: emotionalTone,
        reflection_level: emotionalProfile.reflective,
        percentage: Math.round((depths.length / totalReflections) * 100 * 10) / 10
      };
    });

    // Generate Reflection DNA
    const reflectionDna: string[] = [];

    // Pattern 1: Energy Detection
    const categoryAvgLengths = Object.entries(categoryDepths).reduce((acc, [cat, depths]) => {
      if (depths.length > 0) {
        acc[cat] = depths.reduce((a, b) => a + b, 0) / depths.length;
      }
      return acc;
    }, {} as { [key: string]: number });

    if (Object.keys(categoryAvgLengths).length > 0) {
      const energyTopic = Object.entries(categoryAvgLengths)
        .sort((a, b) => b[1] - a[1])[0];
      const topicName = energyTopic[0].replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      reflectionDna.push(`⚡ Your energy peaks when discussing ${topicName}`);
    }

    // Pattern 2: Processing Style Detection
    const questionCount = countWords(allText, ['?']);
    const storyCount = countPhrases(allText, ['when i', 'i remember', 'there was']);
    const metaphorCount = countWords(allText, ['like', 'as if', 'feels like']);

    if (questionCount > totalReflections * 0.8) {
      reflectionDna.push("🤔 You process life through questioning - always seeking deeper understanding");
    } else if (storyCount > totalReflections * 0.5) {
      reflectionDna.push("📖 You make sense of life through storytelling and memories");
    } else if (metaphorCount > totalReflections * 0.3) {
      reflectionDna.push("🎨 You process experiences through creative metaphors and comparisons");
    }

    // Pattern 3: Emotional Processing Style
    const gratitudeCount = countWords(allText, ['grateful', 'thankful', 'appreciate', 'blessed']);
    const worryCount = countWords(allText, ['worry', 'anxious', 'stressed', 'concerned']);
    const hopeCount = countWords(allText, ['hope', 'wish', 'want', 'dream']);

    if (gratitudeCount > worryCount && gratitudeCount > hopeCount) {
      reflectionDna.push("🙏 Gratitude is your emotional anchor - you naturally find things to appreciate");
    } else if (hopeCount > gratitudeCount && hopeCount > worryCount) {
      reflectionDna.push("✨ You're a natural optimist - future possibilities energize you");
    } else if (worryCount > gratitudeCount) {
      reflectionDna.push("🛡️ You process challenges by anticipating and preparing for difficulties");
    }

    // Pattern 4: Self-Reference Patterns
    const shouldStatements = countPhrases(allText, ['i should', 'i need to', 'i must']);
    const selfCompassion = countPhrases(allText, ["i'm learning", "it's okay", 'i forgive']);

    if (shouldStatements > selfCompassion * 2) {
      reflectionDna.push("⚖️ Your inner critic is active - you often focus on what you 'should' do");
    } else if (selfCompassion > shouldStatements) {
      reflectionDna.push("💝 You practice self-compassion - treating yourself with kindness");
    }

    // Pattern 5: Growth Edge Detection
    const changeWords = countWords(allText, ['change', 'different', 'new', 'grow', 'learn']);
    const stuckWords = countWords(allText, ['same', 'always', 'never', 'stuck', "can't"]);

    if (changeWords > stuckWords) {
      reflectionDna.push("🌱 You're in an active growth phase - embracing change and new perspectives");
    } else if (stuckWords > changeWords) {
      reflectionDna.push("🔄 You're noticing patterns you want to break - awareness is the first step");
    }

    // Pattern 6: Connection Style
    const othersFocus = countWords(allText, ['family', 'friends', 'people', 'others', 'relationships']);
    const selfFocus = countPhrases(allText, ['i feel', 'i think', 'i want', 'my', 'myself']);

    if (othersFocus > selfFocus) {
      reflectionDna.push("🤝 You understand yourself through relationships and connections with others");
    } else {
      reflectionDna.push("🔍 You're developing a strong sense of self through introspection");
    }

    // Limit to top 6 patterns
    const finalReflectionDna = reflectionDna.slice(0, 6);

    // Calculate reflection style metrics
    const totalWordCount = reflections.reduce((sum, r) => sum + (r.word_count || 0), 0);
    const avgWordCount = Math.round(totalWordCount / totalReflections);

    let depthLevel: string;
    if (avgWordCount > 150) depthLevel = "deeply reflective";
    else if (avgWordCount > 100) depthLevel = "moderately reflective";
    else depthLevel = "concise reflector";

    const consistency = totalReflections > 100 ? "highly consistent" :
                       totalReflections > 50 ? "moderately consistent" :
                       "developing consistency";

    // Generate personal insights
    const personalInsights: string[] = [];

    if (coreValues.length > 0) {
      personalInsights.push(`Your reflections reveal '${coreValues[0].value}' as a central theme in your life`);
    }

    const mostInvestedCategory = Object.entries(categoryInsights)
      .sort((a, b) => b[1].total_investment - a[1].total_investment)[0];

    if (mostInvestedCategory) {
      const [catName, catData] = mostInvestedCategory;
      const catDisplay = catName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      personalInsights.push(`You invest the most reflection energy in ${catDisplay}, approaching it with a ${catData.emotional_tone} mindset`);
    }

    // Growth analysis (simplified)
    const growthInsights = {
      depth_trend: "stable",
      focus_shift: null
    };

    return res.status(200).json({
      total_reflections: totalReflections,
      insights: {
        personal_summary: personalInsights.length > 0 ? personalInsights.join('. ') : "Continue reflecting to discover meaningful insights about yourself.",
        core_values: coreValues,
        reflection_dna: finalReflectionDna,
        streak_calendar: streakStats,
        growth_journey: {
          reflection_depth_change: `Your reflection depth has ${growthInsights.depth_trend} over time`,
          focus_evolution: growthInsights.focus_shift || "Your reflection focus has remained consistent",
          emotional_growth: "Growing in self-awareness through consistent reflection"
        },
        category_insights: categoryInsights,
        reflection_style: {
          depth_level: depthLevel,
          consistency: consistency,
          total_words: totalWordCount,
          avg_words_per_reflection: avgWordCount
        }
      }
    });

  } catch (error) {
    console.error('Insights API error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}